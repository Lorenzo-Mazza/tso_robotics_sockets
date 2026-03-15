"""Tests for tso_robotics_sockets client-server integration."""
import json
import socket
import threading
import time

import pytest
import zmq

from tso_robotics_sockets.client import SocketClient
from tso_robotics_sockets.messages.routes import (
    ServerStatus,
    TransportKey,
)
from tso_robotics_sockets.server import SocketServer


def _find_free_port() -> int:
    """Find a free TCP port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _stop_server(server, thread):
    """Signal the server to stop and wait for the thread to exit."""
    server.stop()
    thread.join(timeout=2.0)
    server.reply_socket.close()


@pytest.fixture
def server_port() -> int:
    """Unique free port for each test."""
    return _find_free_port()


@pytest.fixture
def echo_server(server_port: int):
    """Server with a blocking echo route that returns the request payload."""
    context = zmq.Context()
    server = SocketServer(
        ip_address="127.0.0.1",
        port=server_port,
        max_workers=2,
        context=context,
    )

    def echo_handler(message: dict) -> tuple[bool, dict]:
        return True, {"echo": message.get("payload", "empty")}

    server.add_route(
        route_name="echo",
        route_fn=echo_handler,
        blocking=True,
    )

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    time.sleep(0.05)
    yield server
    _stop_server(server, thread)
    context.term()


@pytest.fixture
def client_factory(server_port: int):
    """Factory for SocketClient instances connected to the test server."""
    clients = []

    def factory() -> SocketClient:
        context = zmq.Context()
        client = SocketClient(
            server_address="127.0.0.1",
            server_port=server_port,
            context=context,
        )
        clients.append((client, context))
        return client

    yield factory
    for client, context in clients:
        client.request_socket.close()
        context.term()


@pytest.mark.integration
class TestClientServerBlocking:

    def test_send_request_receives_response(self, echo_server, client_factory):
        client = client_factory()
        response = client.send_request(
            route_name="echo",
            dict_data={"payload": "hello"},
        )
        assert response[TransportKey.STATUS.value] == ServerStatus.FINISHED.value
        assert response["echo"] == "hello"

    def test_unknown_route_returns_error(self, echo_server, client_factory):
        client = client_factory()
        response = client.send_request(route_name="nonexistent")
        assert response[TransportKey.STATUS.value] == ServerStatus.ERROR.value
        assert "not found" in response[TransportKey.ERROR_MSG.value]

    def test_multiple_sequential_requests(self, echo_server, client_factory):
        client = client_factory()
        for index in range(5):
            response = client.send_request(
                route_name="echo",
                dict_data={"payload": f"msg_{index}"},
            )
            assert response["echo"] == f"msg_{index}"

    def test_empty_dict_data_defaults_to_empty(self, echo_server, client_factory):
        client = client_factory()
        response = client.send_request(route_name="echo")
        assert response[TransportKey.STATUS.value] == ServerStatus.FINISHED.value
        assert response["echo"] == "empty"


@pytest.mark.integration
class TestServerRouteDispatch:

    def test_add_route_returns_self_for_chaining(self, server_port: int):
        context = zmq.Context()
        server = SocketServer(
            ip_address="127.0.0.1",
            port=server_port,
            context=context,
        )
        result = server.add_route(
            route_name="test",
            route_fn=lambda msg: (True, {}),
        )
        assert result is server
        server.reply_socket.close()
        context.term()

    def test_error_handler_returns_error_response(self, server_port: int):
        context = zmq.Context()
        server = SocketServer(
            ip_address="127.0.0.1",
            port=server_port,
            context=context,
        )

        def failing_handler(message: dict) -> tuple[bool, dict]:
            raise RuntimeError("handler crashed")

        server.add_route(
            route_name="fail",
            route_fn=failing_handler,
            blocking=True,
        )

        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()
        time.sleep(0.05)

        client_context = zmq.Context()
        client = SocketClient(
            server_address="127.0.0.1",
            server_port=server_port,
            context=client_context,
        )
        response = client.send_request(route_name="fail")
        assert response[TransportKey.STATUS.value] == ServerStatus.ERROR.value
        assert "handler crashed" in response[TransportKey.ERROR_MSG.value]

        client.request_socket.close()
        client_context.term()
        _stop_server(server, thread)
        context.term()


@pytest.mark.integration
class TestServerResponseFormatting:

    def test_create_finished_response(self, server_port: int):
        context = zmq.Context()
        server = SocketServer(
            ip_address="127.0.0.1",
            port=server_port,
            context=context,
        )
        response = json.loads(
            server.create_finished_response({"key": "value"})
        )
        assert response[TransportKey.STATUS.value] == ServerStatus.FINISHED.value
        assert response["key"] == "value"
        server.reply_socket.close()
        context.term()

    def test_create_error_response(self, server_port: int):
        context = zmq.Context()
        server = SocketServer(
            ip_address="127.0.0.1",
            port=server_port,
            context=context,
        )
        response = json.loads(
            server.create_error_response("something failed")
        )
        assert response[TransportKey.STATUS.value] == ServerStatus.ERROR.value
        assert response[TransportKey.ERROR_MSG.value] == "something failed"
        server.reply_socket.close()
        context.term()

    def test_create_processing_response(self, server_port: int):
        context = zmq.Context()
        server = SocketServer(
            ip_address="127.0.0.1",
            port=server_port,
            context=context,
        )
        response = json.loads(
            server.create_processing_response(task_id=42, data={"info": "working"})
        )
        assert response[TransportKey.STATUS.value] == ServerStatus.PROCESSING.value
        assert response[TransportKey.TASK_ID.value] == 42
        assert response["info"] == "working"
        server.reply_socket.close()
        context.term()


@pytest.mark.integration
class TestNonBlockingRoutes:

    def test_non_blocking_route_returns_processing_then_finished(self, server_port: int):
        context = zmq.Context()
        server = SocketServer(
            ip_address="127.0.0.1",
            port=server_port,
            context=context,
        )
        server.add_route(
            route_name="slow",
            route_fn=lambda msg: (True, {"computed": True}),
            blocking=False,
        )
        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()
        time.sleep(0.05)

        client_context = zmq.Context()
        client = SocketClient(
            server_address="127.0.0.1",
            server_port=server_port,
            context=client_context,
        )
        response = client.send_request(route_name="slow")
        assert response[TransportKey.STATUS.value] == ServerStatus.PROCESSING.value
        task_id = response[TransportKey.TASK_ID.value]

        time.sleep(0.1)
        status_response = client.check_task_status(task_id=task_id)
        assert status_response[TransportKey.STATUS.value] == ServerStatus.FINISHED.value
        assert status_response["computed"] is True

        client.request_socket.close()
        client_context.term()
        server.executor.shutdown(wait=True)
        _stop_server(server, thread)
        context.term()

    def test_unknown_task_id_returns_error(self, server_port: int):
        context = zmq.Context()
        server = SocketServer(
            ip_address="127.0.0.1",
            port=server_port,
            context=context,
        )
        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()
        time.sleep(0.05)

        client_context = zmq.Context()
        client = SocketClient(
            server_address="127.0.0.1",
            server_port=server_port,
            context=client_context,
        )
        response = client.check_task_status(task_id=9999)
        assert response[TransportKey.STATUS.value] == ServerStatus.ERROR.value
        assert "9999" in response[TransportKey.ERROR_MSG.value]

        client.request_socket.close()
        client_context.term()
        _stop_server(server, thread)
        context.term()


@pytest.mark.integration
class TestEndToEnd:

    def test_blocking_sum_route(self, server_port: int):
        context = zmq.Context()
        server = SocketServer(
            ip_address="127.0.0.1",
            port=server_port,
            context=context,
        )

        def sum_handler(message: dict) -> tuple[bool, dict]:
            return True, {"sum": sum(message.get("numbers", []))}

        server.add_route(route_name="sum", route_fn=sum_handler, blocking=True)

        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()
        time.sleep(0.05)

        client_context = zmq.Context()
        client = SocketClient(
            server_address="127.0.0.1",
            server_port=server_port,
            context=client_context,
        )

        response = client.send_request(
            route_name="sum",
            dict_data={"numbers": [1, 2, 3, 4, 5]},
        )
        assert response[TransportKey.STATUS.value] == ServerStatus.FINISHED.value
        assert response["sum"] == 15

        response = client.send_request(
            route_name="sum",
            dict_data={"numbers": []},
        )
        assert response["sum"] == 0

        client.request_socket.close()
        client_context.term()
        _stop_server(server, thread)
        context.term()

    def test_non_blocking_sum_route(self, server_port: int):
        context = zmq.Context()
        server = SocketServer(
            ip_address="127.0.0.1",
            port=server_port,
            context=context,
        )

        def sum_handler(message: dict) -> tuple[bool, dict]:
            return True, {"sum": sum(message.get("numbers", []))}

        server.add_route(route_name="sum", route_fn=sum_handler, blocking=False)

        thread = threading.Thread(target=server.run, daemon=True)
        thread.start()
        time.sleep(0.05)

        client_context = zmq.Context()
        client = SocketClient(
            server_address="127.0.0.1",
            server_port=server_port,
            context=client_context,
        )

        response = client.send_request(
            route_name="sum",
            dict_data={"numbers": [10, 20, 30]},
        )
        assert response[TransportKey.STATUS.value] == ServerStatus.PROCESSING.value
        task_id = response[TransportKey.TASK_ID.value]

        time.sleep(0.1)
        status_response = client.check_task_status(task_id=task_id)
        assert status_response[TransportKey.STATUS.value] == ServerStatus.FINISHED.value
        assert status_response["sum"] == 60

        client.request_socket.close()
        client_context.term()
        server.executor.shutdown(wait=True)
        _stop_server(server, thread)
        context.term()
