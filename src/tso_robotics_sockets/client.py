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
        request_timeout_seconds: Send/receive timeout for each request.
            ``None`` (the default) blocks indefinitely, matching the
            behavior of earlier releases.
    """

    def __init__(
        self,
        server_address: str = "localhost",
        server_port: int = 5555,
        context: Optional[zmq.Context] = None,
        request_timeout_seconds: Optional[float] = None,
    ):
        ContextMixin.__init__(self, context=context)
        self.request_timeout_seconds = request_timeout_seconds
        self._connection_address = f"tcp://{server_address}:{server_port}"
        self.request_socket = self._create_socket()

    def _create_socket(self) -> zmq.Socket:
        """Create and connect a REQ socket with the configured timeout."""
        request_socket = self.context.socket(zmq.REQ)
        request_socket.setsockopt(zmq.LINGER, 0)
        if self.request_timeout_seconds is not None:
            timeout_ms = int(self.request_timeout_seconds * 1000)
            request_socket.setsockopt(zmq.RCVTIMEO, timeout_ms)
            request_socket.setsockopt(zmq.SNDTIMEO, timeout_ms)
        request_socket.connect(self._connection_address)
        return request_socket

    def _reset_socket(self) -> None:
        """Replace the REQ socket after a failed request.

        A REQ socket enforces strict send/receive alternation, so a request
        that timed out leaves it permanently unusable; rebuilding the socket
        lets callers retry.
        """
        self.request_socket.close()
        self.request_socket = self._create_socket()

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

        Raises:
            TimeoutError: If the server does not respond within
                ``request_timeout_seconds``. The socket is rebuilt so the
                next request can be attempted.
        """
        if dict_data is None:
            dict_data = {}
        message = {TransportKey.ROUTE_NAME.value: route_name, **dict_data}
        try:
            self.request_socket.send_string(json.dumps(message))
            return json.loads(self.request_socket.recv_string())
        except zmq.error.Again as error:
            self._reset_socket()
            raise TimeoutError(
                f"No response from {self._connection_address} within "
                f"{self.request_timeout_seconds}s for route '{route_name}'."
            ) from error

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
