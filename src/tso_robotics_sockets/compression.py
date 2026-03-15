"""Array compression and decompression utilities for socket transport."""

import base64
import io
from enum import Enum
from typing import Callable, Union

import cv2
import numpy as np


class CompressionType(Enum):
    """Supported array compression formats."""

    PNG = "png"
    NPZ = "npz"
    JPEG = "jpeg"
    JPG = "jpg"
    RAW = "raw"

    def to_compressor(self) -> Callable[..., bytes]:
        """Return the compression function for this format."""
        compressors = {
            CompressionType.PNG.value: compress_png,
            CompressionType.NPZ.value: compress_npz,
            CompressionType.JPEG.value: compress_jpeg,
            CompressionType.JPG.value: compress_jpeg,
            CompressionType.RAW.value: compress_raw,
        }
        return compressors[self.value]

    def to_decompressor(self) -> Callable[[bytes], np.ndarray]:
        """Return the decompression function for this format."""
        decompressors = {
            CompressionType.PNG.value: decompress_png,
            CompressionType.NPZ.value: decompress_npz,
            CompressionType.JPEG.value: decompress_jpeg,
            CompressionType.JPG.value: decompress_jpeg,
            CompressionType.RAW.value: decompress_raw,
        }
        return decompressors[self.value]


def compress_png(data: np.ndarray, png_compression: int = 3) -> bytes:
    """Compress a uint8 array to PNG bytes.

    Args:
        data: Image array (2D grayscale or 3D with C=1/3/4).
        png_compression: PNG compression level (0-9).

    Returns:
        PNG-encoded bytes.
    """
    if data.dtype != np.uint8:
        raise ValueError("For PNG, dtype must be uint8.")
    if not (0 <= data.min() and data.max() <= 255):
        raise ValueError("Array values must be in [0, 255].")
    if data.ndim == 2:
        success, encoded = cv2.imencode(
            ".png",
            data,
            [int(cv2.IMWRITE_PNG_COMPRESSION), png_compression],
        )
    elif data.ndim == 3 and data.shape[2] in [1, 3, 4]:
        if data.shape[2] == 1:
            data = data[:, :, 0]
            success, encoded = cv2.imencode(
                ".png",
                data,
                [int(cv2.IMWRITE_PNG_COMPRESSION), png_compression],
            )
        else:
            data_bgr = cv2.cvtColor(
                data,
                cv2.COLOR_RGB2BGR
                if data.shape[2] == 3
                else cv2.COLOR_RGBA2BGRA,
            )
            success, encoded = cv2.imencode(
                ".png",
                data_bgr,
                [int(cv2.IMWRITE_PNG_COMPRESSION), png_compression],
            )
    else:
        raise ValueError(
            "For PNG, must be 2D or 3D (H, W, C) with C=1/3/4."
        )
    if not success:
        raise ValueError("Failed to encode PNG.")
    return encoded.tobytes()


def compress_jpeg(
    data: np.ndarray,
    jpeg_quality: int = 90,
    extension: str = "jpg",
) -> bytes:
    """Compress a uint8 array to JPEG bytes.

    Args:
        data: Image array (2D grayscale or 3D with C=1/3/4).
        jpeg_quality: JPEG quality (0-100).
        extension: File extension for encoding.

    Returns:
        JPEG-encoded bytes.
    """
    if data.dtype != np.uint8:
        raise ValueError("For JPEG, dtype must be uint8.")
    if not (0 <= data.min() and data.max() <= 255):
        raise ValueError("Array values must be in [0, 255].")
    if data.ndim == 2:
        success, encoded = cv2.imencode(
            f".{extension}",
            data,
            [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality],
        )
    elif data.ndim == 3 and data.shape[2] in [1, 3, 4]:
        if data.shape[2] == 1:
            data = data[:, :, 0]
            success, encoded = cv2.imencode(
                f".{extension}",
                data,
                [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality],
            )
        else:
            data_bgr = cv2.cvtColor(
                data,
                cv2.COLOR_RGB2BGR
                if data.shape[2] == 3
                else cv2.COLOR_RGBA2BGRA,
            )
            success, encoded = cv2.imencode(
                f".{extension}",
                data_bgr,
                [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality],
            )
    else:
        raise ValueError(
            "For JPEG, must be 2D or 3D (H, W, C) with C=1/3/4."
        )
    if not success:
        raise ValueError("Failed to encode JPEG.")
    return encoded.tobytes()


def compress_npz(data: np.ndarray) -> bytes:
    """Compress an array to NPZ bytes.

    Args:
        data: Arbitrary numpy array.

    Returns:
        NPZ-compressed bytes.
    """
    buffer = io.BytesIO()
    np.savez_compressed(buffer, array=data)
    return buffer.getvalue()


def compress_raw(data: np.ndarray) -> bytes:
    """Serialize an array to raw numpy bytes (no compression).

    Args:
        data: Arbitrary numpy array.

    Returns:
        Raw numpy bytes.
    """
    buffer = io.BytesIO()
    np.save(buffer, data, allow_pickle=False)
    return buffer.getvalue()


def encode_bytes_to_base64(data: bytes) -> str:
    """Convert bytes to a base64-encoded UTF-8 string.

    Args:
        data: Raw bytes to encode.

    Returns:
        Base64-encoded string.
    """
    return base64.b64encode(data).decode("utf-8")


def decode_base64_to_bytes(data: str) -> bytes:
    """Convert a base64-encoded string back to bytes.

    Args:
        data: Base64-encoded string.

    Returns:
        Decoded bytes.
    """
    return base64.b64decode(data)


def decompress_png(data_bytes: bytes) -> np.ndarray:
    """Decompress PNG bytes to a numpy array.

    Args:
        data_bytes: PNG-encoded bytes.

    Returns:
        Decoded image array (RGB or RGBA).
    """
    decoded = cv2.imdecode(
        np.frombuffer(data_bytes, np.uint8), cv2.IMREAD_UNCHANGED
    )
    if decoded is None:
        raise ValueError("Failed to decode PNG.")
    if decoded.ndim == 2:
        return decoded
    elif decoded.shape[2] == 3:
        return cv2.cvtColor(decoded, cv2.COLOR_BGR2RGB)
    elif decoded.shape[2] == 4:
        return cv2.cvtColor(decoded, cv2.COLOR_BGRA2RGBA)
    else:
        return decoded


def decompress_jpeg(data_bytes: bytes) -> np.ndarray:
    """Decompress JPEG bytes to a numpy array.

    Args:
        data_bytes: JPEG-encoded bytes.

    Returns:
        Decoded image array (RGB or RGBA).
    """
    decoded = cv2.imdecode(
        np.frombuffer(data_bytes, np.uint8), cv2.IMREAD_UNCHANGED
    )
    if decoded is None:
        raise ValueError("Failed to decode JPEG.")
    if decoded.ndim == 2:
        return decoded
    elif decoded.shape[2] == 3:
        return cv2.cvtColor(decoded, cv2.COLOR_BGR2RGB)
    elif decoded.shape[2] == 4:
        return cv2.cvtColor(decoded, cv2.COLOR_BGRA2RGBA)
    else:
        return decoded


def decompress_npz(data_bytes: bytes) -> np.ndarray:
    """Decompress NPZ bytes to a numpy array.

    Args:
        data_bytes: NPZ-compressed bytes.

    Returns:
        Decompressed array.
    """
    buffer = io.BytesIO(data_bytes)
    loaded = np.load(buffer)
    return loaded["array"]


def decompress_raw(data_bytes: bytes) -> np.ndarray:
    """Deserialize raw numpy bytes to an array.

    Args:
        data_bytes: Raw numpy bytes.

    Returns:
        Deserialized array.
    """
    buffer = io.BytesIO(data_bytes)
    return np.load(buffer)


def compress_array(
    data: np.ndarray,
    method: str,
    jpeg_quality: int = 90,
    png_compression: int = 3,
    as_base64: bool = True,
) -> Union[str, bytes]:
    """Compress a numpy array using the specified method.

    Args:
        data: Array to compress.
        method: Compression method (see ``CompressionType``).
        jpeg_quality: JPEG quality (0-100), used only for JPEG/JPG.
        png_compression: PNG compression level (0-9), used only for PNG.
        as_base64: If ``True``, return a base64 string; otherwise raw bytes.

    Returns:
        Compressed data as base64 string or raw bytes.
    """
    if not isinstance(data, np.ndarray):
        raise ValueError("Input must be a NumPy ndarray.")
    compressor = CompressionType(method).to_compressor()
    if method == CompressionType.PNG.value:
        compressed_bytes = compressor(
            data, png_compression=png_compression
        )
    elif method in [CompressionType.JPEG.value, CompressionType.JPG.value]:
        compressed_bytes = compressor(
            data, jpeg_quality=jpeg_quality, extension=method
        )
    elif method in [CompressionType.NPZ.value, CompressionType.RAW.value]:
        compressed_bytes = compressor(data)
    else:
        raise ValueError(f"Unsupported compression method: {method}")
    return (
        encode_bytes_to_base64(compressed_bytes)
        if as_base64
        else compressed_bytes
    )


def decompress_array(data: Union[str, bytes], method: str) -> np.ndarray:
    """Decompress data back to a numpy array.

    Args:
        data: Compressed data (base64 string or raw bytes).
        method: Compression method used (see ``CompressionType``).

    Returns:
        Decompressed numpy array.
    """
    if isinstance(data, str):
        data = decode_base64_to_bytes(data)
    decompressor = CompressionType(method).to_decompressor()
    if not decompressor:
        raise ValueError(f"Unsupported decompression method: {method}")
    return decompressor(data)
