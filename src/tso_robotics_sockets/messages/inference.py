"""Request/response keys for the inference protocol (GET_OBSERVATION, SEND_ACTION, REGISTER_CLIENT).

The client is the policy (ML model) and the server is the environment
(simulation or real robot). The policy requests observations and sends
actions; the environment executes actions and returns new observations.
"""

from enum import Enum


class InferenceRequestKey(str, Enum):
    """Keys in inference request payloads."""

    CLIENT_NAME = "client_name"
    REQUESTED_KEYS = "requested_keys"
    ACTIONS = "actions"
    ACTION_METADATA = "action_metadata"
    COMPRESSION_TYPE = "compression_type"


class InferenceResponseKey(str, Enum):
    """Keys in inference response payloads."""

    IMAGE_HEIGHT = "image_height"
    IMAGE_WIDTH = "image_width"
    COMPRESSION_TYPE = "compression_type"
    RESET_ENVIRONMENT_INDICES = "reset_environment_indices"
    TIMESTEP = "timestep"
