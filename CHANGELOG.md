# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.5] - 2025-12-10

### Fixed
- BrokenPipeError and ConnectionResetError handling: Graceful shutdown when MCP client closes connection early
- ExceptionGroup support for Python 3.11+ and anyio error handling (recursive nested group detection)
- Improved stdio_server exception handling for better stability
- `__cause__` exception chain detection for wrapped connection errors

### Added
- Comprehensive test suite for connection error handling (9 new tests)

## [0.0.4] - 2025-12-08

### Fixed
- Clean shutdown on Ctrl+C (SIGINT/SIGTERM handling)

## [0.0.3] - 2025-12-08

### Fixed
- Restore Trusted Publisher for PyPI deployment

## [0.0.2] - 2025-12-08

### Changed
- Simplified README with cleaner architecture diagram
- Removed Docker support (not deploying to Docker Hub)
- Cleaned up obsolete documentation files

### Fixed
- CI test failure: Mock `is_cli_installed` in test_creates_temp_files

## [0.0.1] - 2025-12-07

### Added
- **MCP Protocol Support**: Full Model Context Protocol implementation
- **Multi-CLI Support**: Claude, Gemini, Codex, Qwen CLI integration
- **Session Mode**: Conversation context persistence using `session_id` parameter
- **Async Execution**: `run_async` parameter for non-blocking CLI execution
- **Task Management**: `get_task_status` API for tracking async task status
- **Dynamic Agent Registry**: `add_agent` tool for runtime CLI registration
- **Multi-Agent Execution**: `use_agents` tool for parallel multi-CLI requests
- **File-based I/O**: Robust CLI communication via temporary files
- **SQLite Storage**: Persistent task storage with automatic cleanup
- **CI/CD Pipeline**: GitHub Actions workflow for Python 3.10-3.12 testing
- **Comprehensive Test Suite**: 86.5%+ coverage

### Security
- Command injection prevention via argument sanitization
- Environment variable filtering (whitelist/blacklist)
- macOS-specific protections (`DYLD_*` variables blocked)
- Timeout enforcement (1-3600 seconds)
- Security audit integration in CI pipeline
