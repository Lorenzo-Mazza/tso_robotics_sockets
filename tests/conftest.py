"""Shared test fixtures for tso-robotics-sockets."""
from collections.abc import Callable

import numpy as np
import pytest


@pytest.fixture
def rng() -> np.random.Generator:
    """Fixed-seed RNG for reproducible test data."""
    return np.random.default_rng(42)


@pytest.fixture
def random_image_factory(
    rng: np.random.Generator,
) -> Callable[..., np.ndarray]:
    """Factory for random uint8 images."""

    def factory(
        height: int = 64,
        width: int = 64,
        channels: int = 3,
    ) -> np.ndarray:
        if channels == 0:
            return rng.integers(
                low=0, high=256, size=(height, width), dtype=np.uint8
            )
        return rng.integers(
            low=0, high=256, size=(height, width, channels), dtype=np.uint8
        )

    return factory
