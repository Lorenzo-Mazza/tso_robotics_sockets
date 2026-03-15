"""Tests for tso_robotics_sockets.compression module."""
import re
from collections.abc import Callable
from contextlib import nullcontext as does_not_raise

import numpy as np
import pytest

from tso_robotics_sockets.compression import (
    CompressionType,
    compress_array,
    compress_jpeg,
    compress_npz,
    compress_png,
    compress_raw,
    decode_base64_to_bytes,
    decompress_array,
    decompress_jpeg,
    decompress_npz,
    decompress_png,
    decompress_raw,
    encode_bytes_to_base64,
)


@pytest.mark.unit
class TestBase64Encoding:

    def test_roundtrip_preserves_data(self):
        original = b"hello world 12345"
        encoded = encode_bytes_to_base64(original)
        decoded = decode_base64_to_bytes(encoded)
        assert decoded == original

    def test_encoded_is_string(self):
        encoded = encode_bytes_to_base64(b"test")
        assert isinstance(encoded, str)

    def test_empty_bytes_roundtrip(self):
        encoded = encode_bytes_to_base64(b"")
        assert decode_base64_to_bytes(encoded) == b""


@pytest.mark.unit
class TestPNGCompression:

    def test_rgb_roundtrip(self, random_image_factory: Callable[..., np.ndarray]):
        image = random_image_factory(height=32, width=32, channels=3)
        compressed = compress_png(image)
        recovered = decompress_png(compressed)
        assert np.array_equal(image, recovered)

    def test_grayscale_roundtrip(self, random_image_factory: Callable[..., np.ndarray]):
        image = random_image_factory(height=32, width=32, channels=0)
        compressed = compress_png(image)
        recovered = decompress_png(compressed)
        assert np.array_equal(image, recovered)

    def test_single_channel_roundtrip(self, random_image_factory: Callable[..., np.ndarray]):
        image = random_image_factory(height=16, width=16, channels=1)
        compressed = compress_png(image)
        recovered = decompress_png(compressed)
        assert recovered.ndim == 2
        assert np.array_equal(image[:, :, 0], recovered)

    def test_rgba_roundtrip(self, random_image_factory: Callable[..., np.ndarray]):
        image = random_image_factory(height=16, width=16, channels=4)
        compressed = compress_png(image)
        recovered = decompress_png(compressed)
        assert np.array_equal(image, recovered)

    def test_wrong_dtype_raises(self, rng: np.random.Generator):
        float_data = rng.standard_normal((16, 16, 3)).astype(np.float32)
        with pytest.raises(
            ValueError,
            match=re.escape("For PNG, dtype must be uint8."),
        ):
            compress_png(float_data)

    def test_wrong_ndim_raises(self, rng: np.random.Generator):
        data_5d = rng.integers(low=0, high=256, size=(2, 2, 2, 2, 2), dtype=np.uint8)
        with pytest.raises(
            ValueError,
            match=re.escape("For PNG, must be 2D or 3D (H, W, C) with C=1/3/4."),
        ):
            compress_png(data_5d)


@pytest.mark.unit
class TestJPEGCompression:

    def test_rgb_roundtrip_is_lossy(self, random_image_factory: Callable[..., np.ndarray]):
        image = random_image_factory(height=32, width=32, channels=3)
        compressed = compress_jpeg(image)
        recovered = decompress_jpeg(compressed)
        assert recovered.shape == image.shape
        assert recovered.dtype == np.uint8

    def test_grayscale_roundtrip(self, random_image_factory: Callable[..., np.ndarray]):
        image = random_image_factory(height=32, width=32, channels=0)
        compressed = compress_jpeg(image)
        recovered = decompress_jpeg(compressed)
        assert recovered.shape == image.shape

    def test_wrong_dtype_raises(self, rng: np.random.Generator):
        float_data = rng.standard_normal((16, 16, 3)).astype(np.float32)
        with pytest.raises(
            ValueError,
            match=re.escape("For JPEG, dtype must be uint8."),
        ):
            compress_jpeg(float_data)


@pytest.mark.unit
class TestNPZCompression:

    def test_roundtrip_preserves_array(self, rng: np.random.Generator):
        data = rng.standard_normal((10, 20)).astype(np.float32)
        compressed = compress_npz(data)
        recovered = decompress_npz(compressed)
        assert np.array_equal(data, recovered)

    def test_preserves_dtype(self, rng: np.random.Generator):
        data = rng.integers(low=0, high=100, size=(5, 5), dtype=np.int16)
        recovered = decompress_npz(compress_npz(data))
        assert recovered.dtype == np.int16


@pytest.mark.unit
class TestRAWCompression:

    def test_roundtrip_preserves_array(self, rng: np.random.Generator):
        data = rng.standard_normal((8, 12, 3)).astype(np.float64)
        compressed = compress_raw(data)
        recovered = decompress_raw(compressed)
        assert np.array_equal(data, recovered)


@pytest.mark.unit
class TestCompressArrayDispatcher:

    @pytest.mark.parametrize(
        "method, is_lossless",
        [
            ("png", True),
            ("npz", True),
            ("raw", True),
            ("jpeg", False),
        ],
    )
    def test_roundtrip_with_base64(
        self,
        random_image_factory: Callable[..., np.ndarray],
        method: str,
        is_lossless: bool,
    ):
        image = random_image_factory(height=32, width=32, channels=3)
        compressed = compress_array(data=image, method=method, as_base64=True)
        assert isinstance(compressed, str)
        recovered = decompress_array(data=compressed, method=method)
        if is_lossless:
            assert np.array_equal(image, recovered)
        else:
            assert recovered.shape == image.shape

    def test_returns_bytes_when_base64_disabled(
        self, random_image_factory: Callable[..., np.ndarray]
    ):
        image = random_image_factory(height=16, width=16, channels=3)
        compressed = compress_array(data=image, method="png", as_base64=False)
        assert isinstance(compressed, bytes)

    def test_non_ndarray_raises(self):
        with pytest.raises(
            ValueError,
            match=re.escape("Input must be a NumPy ndarray."),
        ):
            compress_array(data=[1, 2, 3], method="raw")

    def test_unsupported_method_raises(self, random_image_factory: Callable[..., np.ndarray]):
        image = random_image_factory()
        with pytest.raises(ValueError):
            compress_array(data=image, method="bmp")


@pytest.mark.unit
class TestCompressionTypeEnum:

    def test_all_methods_have_compressor(self):
        for compression_type in CompressionType:
            assert callable(compression_type.to_compressor())

    def test_all_methods_have_decompressor(self):
        for compression_type in CompressionType:
            assert callable(compression_type.to_decompressor())
