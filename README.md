# tso-robotics-sockets

[![Tests](https://github.com/Lorenzo-Mazza/tso_robotics_sockets/actions/workflows/test.yml/badge.svg)](https://github.com/Lorenzo-Mazza/tso_robotics_sockets/actions/workflows/test.yml)
[![PyPI](https://img.shields.io/pypi/v/tso-robotics-sockets)](https://pypi.org/project/tso-robotics-sockets/)
[![Python](https://img.shields.io/pypi/pyversions/tso-robotics-sockets)](https://pypi.org/project/tso-robotics-sockets/)

Lightweight ZMQ socket communication for robotics inference servers.

Provides a `SocketClient` / `SocketServer` pair plus array compression utilities for sending images and numpy arrays over ZeroMQ.

## Installation

```bash
pip install tso-robotics-sockets
```

## Quick start

```python
from tso_robotics_sockets import SocketServer, SocketClient, ServerRoute

# Server
server = SocketServer(ip_address="0.0.0.0", port=5555)
server.add_route("echo", lambda msg: (True, msg), blocking=True)
server.run()

# Client (separate process)
client = SocketClient(server_address="localhost", server_port=5555)
response = client.send_request(route_name="echo", dict_data={"hello": "world"})
client.close()
```