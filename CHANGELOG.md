# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-03-15

### Added
- Python 3.13 support (CI matrix and classifiers)
- `RequestKey.REQUESTED_KEYS` — for simulation clients to specify which observation keys to return
- `RequestKey.ACTIONS` — for sending action dicts (metadata-driven format)
- `RequestKey.CLIENT_NAME` — for client registration with simulation servers
- `ResponseKey.RESET_ENVIRONMENT_INDICES` — indices of environments that were reset
- `ResponseKey.TIMESTEP` — current simulation timestep
- `ResponseKey.IMAGE_HEIGHT` / `ResponseKey.IMAGE_WIDTH` — image dimensions in responses
- PyPI and CI badges in README

### Changed
- `ResponseKey.HEIGHT` renamed to `ResponseKey.IMAGE_HEIGHT` (matches production servers)
- `ResponseKey.WIDTH` renamed to `ResponseKey.IMAGE_WIDTH` (matches production servers)

### Changed
- `SocketServer.run()` now uses `zmq.Poller` instead of blocking `recv_string()`, enabling clean shutdown via new `stop()` method

### Fixed
- Server thread could not be stopped cleanly — cross-thread socket close caused segfaults (3.11+) and hangs (3.10) due to ZMQ thread-safety constraints

### Added
- Integration End-To-End tests `test_blocking_sum_route` and `test_non_blocking_sum_route`  
### Removed
- `ResponseKey.RESULT` — was only used by deleted example routes

## [0.1.0] - 2026-03-15

### Added
- `SocketClient` — ZMQ REQ client for sending requests to robotics servers.
- `SocketServer` — ZMQ REP server with blocking and non-blocking route dispatch via ThreadPoolExecutor.
- `ContextMixin` — shared ZMQ context singleton for multi-socket processes.
- `compress_array` / `decompress_array` — NumPy array serialization with PNG, JPEG, NPZ, and RAW methods, with optional base64 encoding.
- `CompressionType` enum for selecting compression method.
- `ServerRoute` enum — standardized route names (GET_OBSERVATION, SEND_ACTION, REGISTER_CLIENT, COMPUTE_STEREO).
- `ServerStatus` enum — response status values (FINISHED, ERROR, PROCESSING, WAITING_ACTION, CREATING_ENV).
- `RequestKey` enum — 14 standardized request payload keys.
- `ResponseKey` enum — 18 standardized response payload keys.

### Notes
- Zero dependency on PyTorch, TensorFlow, or any ML framework.
- Designed for use on both training machines (with ML stack) and robot PCs (minimal install).

[Unreleased]: https://github.com/Lorenzo-Mazza/tso_robotics_sockets/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/Lorenzo-Mazza/tso_robotics_sockets/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/Lorenzo-Mazza/tso_robotics_sockets/releases/tag/v0.1.0