"""Request/response keys for the stereo computation protocol (COMPUTE_STEREO)."""

from enum import Enum


class StereoRequestKey(str, Enum):
    """Keys in stereo computation request payloads."""

    LEFT_IMG = "left_img"
    RIGHT_IMG = "right_img"
    REQUEST_DISPARITY = "request_disparity"
    REQUEST_DEPTH = "request_depth"
    REQUEST_POINT_CLOUD = "request_point_cloud"
    COMPRESSION_TYPE = "compression_type"


class StereoResponseKey(str, Enum):
    """Keys in stereo computation response payloads."""

    DISPARITY_MAP = "disparity_map"
    DEPTH_MAP = "depth_map"
    POINT_CLOUD = "point_cloud"
    COMPRESSION_TYPE = "compression_type"
