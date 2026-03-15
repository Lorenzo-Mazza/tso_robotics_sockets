"""ZMQ socket server with blocking and non-blocking route handling."""

import json
import threading
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Optional

import zmq

from tso_robotics_sockets.base import ContextMixin
from tso_robotics_sockets.messages.routes import (
    ServerRoute,
    ServerStatus,
    TransportKey,
)


class SocketServer(ContextMixin):
    """ZMQ REP server with support for blocking and non-blocking routes.

    Blocking routes return immediately. Non-blocking routes submit work
    to a thread pool and return a task id that clients can poll.

    Args:
        ip_address: Interface to bind.
        port: TCP port to bind.
        max_workers: Thread pool size for non-blocking routes.
        context: Shared zmq context; if ``None``, the process singleton
            is used.
    """

    def __init__(
        self,
        ip_address: str = "localhost",
        port: int = 5555,
        max_workers: int = 4,
        context: Optional[zmq.Context] = None,
    ):
        ContextMixin.__init__(self, context=context)

        self.reply_socket = self.context.socket(zmq.REP)
        self.reply_socket.setsockopt(zmq.LINGER, 0)
        self.reply_socket.bind(f"tcp://{ip_address}:{port}")
        self.routes: Dict[str, Callable] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.pending_tasks: Dict[int, Any] = {}
        self.task_counter: int = 0
        self._stop_event = threading.Event()

    def _create_response(
        self, route_fn: Callable, blocking: bool = True
    ) -> Callable:
        """Wrap a route function with response formatting.

        Args:
            route_fn: Handler that returns ``(success, data)``.
            blocking: If ``True``, execute synchronously; otherwise
                submit to the thread pool.

        Returns:
            Wrapped callable that produces a JSON response string.
        """

        def response_fn(json_message: dict) -> str:
            if blocking:
                try:
                    success, data = route_fn(json_message)
                    return (
                        self.create_finished_response(data)
                        if success
                        else self.create_error_response(data)
                    )
                except Exception as error:  # noqa: BLE001
                    return self.create_error_response(f"{error}")
            task_id = self.task_counter
            self.task_counter += 1
            future = self.executor.submit(route_fn, json_message)
            self.pending_tasks[task_id] = future
            return self.create_processing_response(task_id, {})

        return response_fn

    def create_error_response(self, error_message: str) -> str:
        """Build a JSON error response.

        Args:
            error_message: Human-readable error description.

        Returns:
            JSON-encoded error response string.
        """
        return json.dumps(
            {
                TransportKey.STATUS.value: ServerStatus.ERROR.value,
                TransportKey.ERROR_MSG.value: error_message,
            }
        )

    def create_finished_response(
        self, data: Dict[str, Any]
    ) -> str:
        """Build a JSON success response.

        Args:
            data: Response payload to merge with the status.

        Returns:
            JSON-encoded success response string.
        """
        return json.dumps(
            {TransportKey.STATUS.value: ServerStatus.FINISHED.value, **data}
        )

    def create_processing_response(
        self, task_id: int, data: Dict[str, Any]
    ) -> str:
        """Build a JSON processing response for a non-blocking task.

        Args:
            task_id: Identifier for the submitted task.
            data: Additional payload to include.

        Returns:
            JSON-encoded processing response string.
        """
        return json.dumps(
            {
                TransportKey.STATUS.value: ServerStatus.PROCESSING.value,
                TransportKey.TASK_ID.value: task_id,
                **data,
            }
        )

    def add_route(
        self,
        route_name: str,
        route_fn: Callable,
        blocking: bool = True,
    ) -> "SocketServer":
        """Register a route handler.

        Args:
            route_name: Name of the route.
            route_fn: Handler returning ``(success, data)`` tuple.
            blocking: Whether to execute synchronously.

        Returns:
            Self, for method chaining.
        """
        self.routes[route_name] = self._create_response(
            route_fn, blocking
        )
        return self

    def check_task_status(self, task_id: int) -> str:
        """Check the status of a non-blocking task.

        Args:
            task_id: Task identifier to check.

        Returns:
            JSON-encoded status response.
        """
        if task_id not in self.pending_tasks:
            return self.create_error_response(
                f"Task id {task_id} not found"
            )
        future = self.pending_tasks[task_id]
        if future.done():
            try:
                success, data = future.result()
                del self.pending_tasks[task_id]
                return (
                    self.create_finished_response(data)
                    if success
                    else self.create_error_response(data)
                )
            except Exception as error:  # noqa: BLE001
                del self.pending_tasks[task_id]
                return self.create_error_response(f"{error}")
        return self.create_processing_response(task_id, {})

    def stop(self) -> None:
        """Signal the server to stop its main loop."""
        self._stop_event.set()

    def run(self) -> None:
        """Start the server main loop.

        Listens for JSON messages, dispatches to registered routes,
        and handles task status polling.  Uses a poller so the loop
        can be interrupted cleanly via :meth:`stop`.
        """
        poller = zmq.Poller()
        poller.register(self.reply_socket, zmq.POLLIN)
        while not self._stop_event.is_set():
            socks = dict(poller.poll(timeout=100))
            if self.reply_socket not in socks:
                continue
            try:
                message = self.reply_socket.recv_string(zmq.NOBLOCK)
                json_message = json.loads(message)
                route_name = json_message[TransportKey.ROUTE_NAME.value]
                if route_name == ServerRoute.TASK_STATUS.value:
                    response = self.check_task_status(
                        json_message[TransportKey.TASK_ID.value]
                    )
                elif route_name in self.routes:
                    response = self.routes[route_name](json_message)
                else:
                    response = self.create_error_response(
                        f"Route {route_name} not found"
                    )
                self.reply_socket.send_string(response)
            except Exception as error:
                if self.reply_socket.closed:
                    break
                self.reply_socket.send_string(
                    self.create_error_response(f"{error}")
                )
