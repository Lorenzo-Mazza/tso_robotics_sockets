"""Shared route, status, and transport-level keys for all server types."""

from enum import Enum


class ServerRoute(str, Enum):
    """Route names for client-server communication."""

    TASK_STATUS = "task_status"
    GET_OBSERVATION = "get_observation"
    SEND_ACTION = "send_action"
    REGISTER_CLIENT = "register_client"
    COMPUTE_STEREO = "compute_stereo"


class ServerStatus(str, Enum):
    """Response status values."""

    FINISHED = "FINISHED"
    ERROR = "ERROR"
    PROCESSING = "PROCESSING"
    WAITING_ACTION = "WAITING_ACTION"
    CREATING_ENV = "CREATING_ENV"


class TransportKey(str, Enum):
    """Keys used by the socket transport layer itself (shared across all protocols)."""

    ROUTE_NAME = "route_name"
    TASK_ID = "task_id"
    STATUS = "status"
    ERROR_MSG = "error_msg"
