"""ZMQ socket client for communicating with robotics servers."""

import json
from typing import Optional

import zmq

from tso_robotics_sockets.base import ContextMixin
from tso_robotics_sockets.messages.routes import ServerRoute, TransportKey


class SocketClient(ContextMixin):
    """ZMQ REQ client for sending requests to a socket server.

    Supports both blocking requests and task status polling for
    non-blocking server operations.

    Args:
        server_address: Server hostname or IP.
        server_port: Server TCP port.
        context: Shared zmq context; if ``None``, the process singleton
            is used.
    """

    def __init__(
        self,
        server_address: str = "localhost",
        server_port: int = 5555,
        context: Optional[zmq.Context] = None,
    ):
        ContextMixin.__init__(self, context=context)
        self.request_socket = self.context.socket(zmq.REQ)
        self.request_socket.setsockopt(zmq.LINGER, 0)
        connection_address = f"tcp://{server_address}:{server_port}"
        self.request_socket.connect(connection_address)

    def send_request(
        self,
        route_name: str,
        dict_data: Optional[dict] = None,
    ) -> dict:
        """Send a JSON request and return the parsed response.

        Args:
            route_name: Server route to call.
            dict_data: Additional payload merged into the request.

        Returns:
            Parsed JSON response from the server.
        """
        if dict_data is None:
            dict_data = {}
        message = {TransportKey.ROUTE_NAME.value: route_name, **dict_data}
        self.request_socket.send_string(json.dumps(message))
        return json.loads(self.request_socket.recv_string())

    def check_task_status(self, task_id: int) -> dict:
        """Poll the status of a non-blocking server task.

        Args:
            task_id: Task identifier returned by the server.

        Returns:
            Task status response with current state and result if finished.
        """
        return self.send_request(
            ServerRoute.TASK_STATUS.value,
            {TransportKey.TASK_ID.value: task_id},
        )

    def close(self) -> None:
        """Close the socket and terminate the context."""
        self.request_socket.close()
        self.context.term()
