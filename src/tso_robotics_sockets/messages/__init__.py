"""Wire protocol messages for robotics socket communication."""

from tso_robotics_sockets.messages.routes import (
    ServerRoute,
    ServerStatus,
    TransportKey,
)
from tso_robotics_sockets.messages.inference import (
    InferenceRequestKey,
    InferenceResponseKey,
)
from tso_robotics_sockets.messages.stereo import (
    StereoRequestKey,
    StereoResponseKey,
)

__all__ = [
    "ServerRoute",
    "ServerStatus",
    "TransportKey",
    "InferenceRequestKey",
    "InferenceResponseKey",
    "StereoRequestKey",
    "StereoResponseKey",
]
