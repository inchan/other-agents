# Other Agents MCP Server

## Project Overview
**Type:** Python / MCP Server (Model Context Protocol)
**Purpose:** Acts as a bridge between MCP clients (like Claude Desktop or IDEs) and local AI CLI tools (e.g., `claude`, `gemini`, `codex`, `qwen`). It standardizes communication using a file-based I/O mechanism to ensure safe, stateless execution.

## Key Technologies
- **Language:** Python 3.10+ (3.12 recommended)
- **Protocol:** MCP SDK (Model Context Protocol)
- **Testing:** `pytest`, `pytest-asyncio`, `pytest-cov`
- **Linting/Formatting:** `black`, `ruff`
- **Communication:** `stdio` (JSON-RPC) for Client-Server, File I/O for Server-CLI.

## Architecture
The data flow follows this path:
1.  **MCP Client:** Sends a request (e.g., `use_agent`) via JSON-RPC over stdio.
2.  **MCP Server (`other_agents_mcp`):** Receives the request and validates it.
3.  **File Handler:** Writes the message to a temporary input file.
4.  **CLI Execution:** The server executes the target CLI tool, pointing it to the input file.
5.  **Response:** The CLI writes to an output file; the server reads it and returns the result to the client.

## Directory Structure
- `src/other_agents_mcp/`: Source code for the server.
    - `server.py`: Main entry point and tool definitions (`list_agents`, `call_tool`).
    - `cli_manager.py`: Manages available CLI tools.
    - `file_handler.py`: Handles the file-based communication logic.
    - `cli_registry.py`: Dynamic registry for CLI configurations.
- `tests/`: Comprehensive test suite.
    - `mcp-validation/`: Specific validation tests ensuring protocol compliance (Phase 1-3).
- `docs/`: Documentation, including `INSTRUCTIONS.md` and `REQUIREMENTS.md` for the automated spec workflow.
- `.artifacts/`: (Local only) Contains development artifacts like test reports, plans, and analysis docs. Not tracked by git.

## Building and Running

### Installation
```bash
# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

### Running the Server
```bash
# Direct execution (Standard IO)
python -m other_agents_mcp.server

# With MCP Inspector (for debugging)
npx @modelcontextprotocol/inspector ./venv/bin/python -m other_agents_mcp.server
```

### Testing
The project has strict testing requirements with high coverage goals.

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=src --cov-report=term-missing

# Run validation suite
pytest tests/mcp-validation/ -v
```

## Development Conventions

### Coding Style
- **Formatter:** `black` (line-length: 100)
- **Linter:** `ruff` (line-length: 100, target: py310)
- **Type Hinting:** Strictly enforced. Use `typing` module.

### Testing Standards
- **Coverage:** maintain >80% coverage.
- **Validation:** Any protocol-level changes must pass the `tests/mcp-validation` suite.
- **Mocking:** Use `unittest.mock` or `pytest-mock` to avoid spawning actual CLI subprocesses during unit tests.

### Documentation Workflow
- **Source of Truth:** `docs/INSTRUCTIONS.md` contains natural language requirements.
- **Generated Spec:** `docs/REQUIREMENTS.md` is auto-updated based on instructions (per `CLAUDE.md`).
- **Gemini Context:** Use `GEMINI.md` (this file) to understand the project context.

## Available Tools (MCP)
1.  `list_agents`: Returns a list of installed and configured AI CLI tools.
2.  `use_agent`: Sends a prompt to a specific CLI.
    - Args: `cli_name` (str), `message` (str), `system_prompt` (optional), `skip_git_repo_check` (optional bool), `args` (optional list).
3.  `add_agent`: Dynamically adds a new CLI tool configuration at runtime.

## Critical Rules for AI Agents
1.  **Do not break existing tests:** Run `pytest` after any modification.
2.  **Respect File I/O:** All CLI communication *must* go through the file handler pattern defined in `file_handler.py` to ensure safety.
3.  **Check `pyproject.toml`:** Refer to this file for the authoritative source on dependencies and tool configurations.
