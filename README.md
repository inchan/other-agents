# Other Agents

[![PyPI version](https://badge.fury.io/py/other-agents-mcp.svg)](https://pypi.org/project/other-agents-mcp/)
[![CI](https://github.com/inchan/other-agents/actions/workflows/ci.yml/badge.svg)](https://github.com/inchan/other-agents/actions/workflows/ci.yml)
[![Python](https://img.shields.io/pypi/pyversions/other-agents-mcp.svg)](https://pypi.org/project/other-agents-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-Compatible-blue.svg)](https://modelcontextprotocol.io/)

> **A unified MCP server to orchestrate multiple AI CLI tools from a single interface.**

Other Agents is an [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) server that enables seamless communication with multiple AI command-line tools—Claude, Gemini, Codex, and Qwen—through a standardized protocol. Stop switching between different CLIs; use them all from one place.

---

## Why Other Agents?

When working with AI coding assistants, you often want to:
- Get a **second opinion** from a different AI model
- **Compare responses** across multiple AI tools
- **Delegate specialized tasks** to the most suitable AI
- **Maintain context** across multiple interactions

Other Agents solves this by providing a unified MCP interface that lets any MCP-compatible client (like Claude Desktop or Claude Code) communicate with multiple AI CLI tools.

```
┌─────────────────────┐
│   MCP Client        │
│ (Claude Desktop)    │
└─────────┬───────────┘
          │ MCP Protocol
          ▼
┌─────────────────────┐
│  Other Agents MCP   │
│       Server        │
└─────────┬───────────┘
          │ File-based I/O
          ▼
┌─────────────────────────────────────┐
│  AI CLI Tools                       │
│  ┌───────┐ ┌───────┐ ┌───────┐     │
│  │Claude │ │Gemini │ │ Codex │ ... │
│  └───────┘ └───────┘ └───────┘     │
└─────────────────────────────────────┘
```

---

## Quick Start

### 1. Install

```bash
# Using uvx (recommended - no installation needed)
uvx other-agents-mcp

# Or install via pip
pip install other-agents-mcp
```

### 2. Configure Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "other-agents": {
      "command": "uvx",
      "args": ["other-agents-mcp"]
    }
  }
}
```

### 3. Start Using

In Claude Desktop, you can now say:

```
"Ask Gemini to review this code"
"Get Codex's opinion on this architecture"
"Send this question to all available AI tools"
```

---

## Features

| Feature | Description |
|---------|-------------|
| **🤖 Multi-Agent Support** | Claude, Gemini, Codex (Cursor), Qwen out of the box |
| **📡 Broadcast Mode** | Send the same prompt to all agents simultaneously |
| **⚡ Async Execution** | Run long tasks in background, poll for results |
| **💬 Session Mode** | Maintain conversation context across interactions |
| **🔧 Dynamic Registration** | Add custom CLI tools at runtime |
| **🔒 Secure Communication** | File-based I/O with automatic cleanup |

---

## Supported AI CLI Tools

| CLI | Command | Status | Notes |
|-----|---------|--------|-------|
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | `claude` | ✅ Ready | Anthropic's official CLI |
| [Gemini CLI](https://github.com/google-gemini/gemini-cli) | `gemini` | ✅ Ready | Google's Gemini CLI |
| [Codex](https://github.com/openai/codex) | `codex` | ✅ Ready | OpenAI Codex (via Cursor) |
| [Qwen](https://github.com/QwenLM/Qwen) | `qwen` | ✅ Ready | Alibaba's Qwen CLI |

> **Note**: Each CLI tool must be installed separately on your system.

---

## Installation

### Option 1: PyPI (Recommended)

```bash
# Run directly with uvx (no install required)
uvx other-agents-mcp

# Or install globally
pip install other-agents-mcp

# Or install in a virtual environment
python -m venv venv
source venv/bin/activate
pip install other-agents-mcp
```

### Option 2: Smithery

```bash
npx @smithery/cli install other-agents-mcp --client claude
```

### Option 3: Docker

```bash
docker pull inchan/other-agents-mcp:latest
docker run -it inchan/other-agents-mcp
```

### Option 4: From Source

```bash
git clone https://github.com/inchan/other-agents.git
cd other-agents
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

---

## Configuration

### Claude Desktop

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "other-agents": {
      "command": "uvx",
      "args": ["other-agents-mcp"]
    }
  }
}
```

### Claude Code

Add to `.claude/settings.local.json` in your project:

```json
{
  "mcpServers": {
    "other-agents": {
      "command": "uvx",
      "args": ["other-agents-mcp"]
    }
  }
}
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_STORAGE_TYPE` | Task storage backend (`memory` or `sqlite`) | `memory` |
| `OPENAI_API_KEY` | Required for Qwen CLI | - |

---

## Available MCP Tools

### `list_agents`

Returns a list of configured AI CLI tools with their installation status.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `check_auth` | boolean | If `true`, verifies authentication status for each CLI |

**Example Response:**
```json
{
  "agents": [
    {"name": "claude", "installed": true, "version": "1.0.0"},
    {"name": "gemini", "installed": true, "version": "0.1.5"},
    {"name": "codex", "installed": false},
    {"name": "qwen", "installed": true}
  ]
}
```

---

### `use_agent`

Sends a prompt to a specific AI CLI and returns the response.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `cli_name` | string | ✅ | Target CLI: `claude`, `gemini`, `codex`, `qwen` |
| `message` | string | ✅ | The prompt to send |
| `run_async` | boolean | | Run in background, return `task_id` immediately |
| `session_id` | string | | Enable session mode for context persistence |
| `resume` | boolean | | Continue from previous session (requires `session_id`) |
| `system_prompt` | string | | Custom system prompt |
| `timeout` | number | | Timeout in seconds |
| `args` | array | | Additional CLI arguments |

**Basic Example:**
```json
{
  "name": "use_agent",
  "arguments": {
    "cli_name": "gemini",
    "message": "Explain the difference between async and await in Python"
  }
}
```

**Async Example:**
```json
{
  "name": "use_agent",
  "arguments": {
    "cli_name": "claude",
    "message": "Analyze this large codebase for security issues",
    "run_async": true
  }
}
// Returns: {"task_id": "abc-123"}
```

**Session Example:**
```json
{
  "name": "use_agent",
  "arguments": {
    "cli_name": "claude",
    "message": "What did we discuss earlier?",
    "session_id": "my-session",
    "resume": true
  }
}
```

---

### `use_agents`

Broadcasts a prompt to multiple AI CLIs simultaneously and collects all responses.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `message` | string | ✅ | The prompt to send to all agents |
| `cli_names` | array | | Specific CLIs to target (omit for all available) |
| `timeout` | number | | Timeout in seconds for each CLI |

**Example:**
```json
{
  "name": "use_agents",
  "arguments": {
    "message": "Review this code for potential bugs",
    "cli_names": ["claude", "gemini", "codex"]
  }
}
```

**Response:**
```json
{
  "responses": [
    {"cli": "claude", "status": "success", "response": "..."},
    {"cli": "gemini", "status": "success", "response": "..."},
    {"cli": "codex", "status": "error", "error": "CLI not installed"}
  ]
}
```

---

### `get_task_status`

Retrieves the status and result of an async task.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `task_id` | string | ✅ | The task ID returned by `use_agent` |

**Response (In Progress):**
```json
{
  "task_id": "abc-123",
  "status": "running",
  "progress": "Processing..."
}
```

**Response (Completed):**
```json
{
  "task_id": "abc-123",
  "status": "completed",
  "result": "Here is the analysis..."
}
```

---

### `add_agent`

Dynamically registers a new AI CLI tool at runtime.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `name` | string | ✅ | Unique identifier for the CLI |
| `command` | string | ✅ | The command to execute |
| `timeout` | number | | Default timeout in seconds |
| `env_vars` | object | | Environment variables to set |
| `supported_args` | array | | List of supported CLI arguments |

**Example:**
```json
{
  "name": "add_agent",
  "arguments": {
    "name": "my-custom-ai",
    "command": "my-ai-cli",
    "timeout": 120
  }
}
```

---

## Usage Examples

### Example 1: Code Review from Multiple AIs

```
User: "Ask Claude and Gemini to review this function for bugs"

→ use_agents(
    message="Review this function for potential bugs: [code]",
    cli_names=["claude", "gemini"]
  )
```

### Example 2: Long-Running Analysis

```
User: "Have Codex analyze this entire repository"

→ use_agent(
    cli_name="codex",
    message="Analyze the architecture of this codebase",
    run_async=true
  )

# Later...
→ get_task_status(task_id="abc-123")
```

### Example 3: Contextual Conversation

```
# First message
→ use_agent(
    cli_name="claude",
    message="Let's analyze the auth module",
    session_id="auth-review"
  )

# Follow-up (context preserved)
→ use_agent(
    cli_name="claude",
    message="What security issues did you find?",
    session_id="auth-review",
    resume=true
  )
```

---

## Development

### Running the Server

```bash
# Activate virtual environment
source venv/bin/activate

# Run server directly
python -m other_agents_mcp.server

# Run with MCP Inspector (for debugging)
npx @modelcontextprotocol/inspector python -m other_agents_mcp.server
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src/other_agents_mcp --cov-report=term-missing

# Run specific test suite
pytest tests/mcp-validation/ -v
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
ruff check src/ tests/
```

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) by Anthropic
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

---

<p align="center">
  <sub>Built with ❤️ for the AI development community</sub>
</p>
