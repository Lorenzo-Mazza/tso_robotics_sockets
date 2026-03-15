"""Tests for tso_robotics_sockets.base module."""
from unittest.mock import MagicMock

import pytest
import zmq

from tso_robotics_sockets.base import ContextMixin


@pytest.mark.unit
class TestContextMixin:

    def test_creates_context_when_none_provided(self):
        mixin = ContextMixin()
        assert mixin.context is not None
        assert isinstance(mixin.context, zmq.Context)

    def test_uses_provided_context(self):
        custom_context = zmq.Context()
        mixin = ContextMixin(context=custom_context)
        assert mixin.context is custom_context
        custom_context.term()

    def test_default_uses_singleton_instance(self):
        mixin_a = ContextMixin()
        mixin_b = ContextMixin()
        assert mixin_a.context is mixin_b.context
