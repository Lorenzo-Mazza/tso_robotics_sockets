"""ZMQ context mixin for shared socket context management."""

from typing import Optional

import zmq


class ContextMixin:
    """Cooperative mixin that provides a shared zmq.Context instance.

    If no context is supplied, the process-wide singleton from
    ``zmq.Context.instance()`` is used so that all objects in the
    process share a single context.

    Args:
        context: Existing zmq context to reuse. If ``None``, the
            process-wide singleton is used.
    """

    def __init__(self, context: Optional[zmq.Context] = None):
        self.context: zmq.Context = context or zmq.Context.instance()
