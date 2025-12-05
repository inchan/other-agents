# Other Agents MCP Server

> **Version 2.1** - Session Mode Support

MCP (Model Context Protocol) 서버로 로컬에 설치된 AI CLI 도구들과 **파일 기반**으로 통신합니다.

## 🎯 Quick Start - 사용 예시

Claude Code에서 자연어로 다른 AI에게 작업을 요청할 수 있습니다:

```
"codex에게 이 코드 리뷰 요청해줘"
→ use_agent(cli_name="codex", message="...")

"gemini한테 물어봐줘: 이 함수 최적화 방법은?"
→ use_agent(cli_name="gemini", message="...")

"claude, gemini, codex 모두에게 의견 물어봐"
→ use_agents(cli_names=["claude", "gemini", "codex"], message="...")

"모든 AI에게 리뷰 요청"
→ use_agents(message="...", cli_names 생략)
```

### 지원하는 AI CLI
- **claude** - Claude AI
- **gemini** - Google Gemini
- **codex** - Cursor의 Codex
- **qwen** - Alibaba Qwen

## ✨ Features

### Core Features
- ✅ **list_agents**: 설치된 AI CLI 도구 목록 조회
- ✅ **use_agent**: AI CLI에 메시지 보내고 응답 받기 (동기 방식)
- ✅ **비동기 작업 실행**: `use_agent(run_async=true)`와 `get_task_status`를 통해 긴 작업을 백그라운드에서 처리
- ✅ **영속적 작업 저장소**: SQLite를 사용하여 서버가 재시작되어도 작업 상태 유지 (선택 사항)
- ✅ **add_agent**: 런타임에 새로운 AI CLI 추가 (v2.0)
- ✅ **다양한 CLI 지원**: Claude, Gemini, Codex, Qwen 등 주요 AI 코딩 CLI 도구 지원

### v2.1 New: Session Mode 🎉
- ✅ **Stateless/Session 모드 자동 전환**: session_id 유무로 자동 판단
- ✅ **컨텍스트 유지**: 이전 대화 내용 기억 및 재사용
- ✅ **다중 세션 격리**: 여러 세션 동시 진행 가능
- ✅ **CLI별 세션 전략**: Claude (UUID), Gemini/Qwen (latest), Codex (last)

### Other Features
- ✅ **환경 변수 지원**: Qwen 등 API 키가 필요한 CLI 지원
- ✅ **skip_git_repo_check**: Codex CLI Git 저장소 체크 스킵 (선택)
- ✅ **파일 기반 통신**: 안전한 임시 파일 처리
- ✅ **상세 로깅 시스템**: 디버깅 및 모니터링 용이
- ✅ **MCP 서버 통합**: MCP SDK 1.22.0과 완벽 호환

## 📋 Supported CLIs

| CLI | Command | 환경 변수 | 특이사항 | 상태 |
|-----|---------|----------|---------|------|
| Claude Code | `claude` | - | - | ✅ 지원 |
| Gemini CLI | `gemini` | - | - | ✅ 지원 |
| OpenAI Codex | `codex` | - | skip_git_check 지원 | ✅ 지원 |
| Qwen Code | `qwen` | OPENAI_API_KEY 등 | 환경 변수 필요 | ✅ 지원 |

## 🚀 Installation

### Prerequisites
- Python 3.10 or higher
- Node.js (for MCP Inspector)

### Setup

```bash
# 1. Python 3.12 설치 (권장)
brew install python@3.12

# 2. 가상 환경 생성
python3.12 -m venv venv
source venv/bin/activate

# 3. 패키지 설치 (개발 모드)
pip install -e .

# 4. 개발 의존성 설치 (선택)
pip install -e ".[dev]"
```

### Verify Installation

```bash
# MCP SDK 설치 확인
pip show mcp

# 서버 import 테스트
python -c "from other_agents_mcp.server import app; print('Server:', app.name)"
```

## 🧪 Development

### Running the MCP Server

```bash
# Activate virtual environment
source venv/bin/activate

# Run server directly (for debugging)
python -m other_agents_mcp.server

# Run with MCP Inspector (for testing)
npx @modelcontextprotocol/inspector ./venv/bin/python -m other_agents_mcp.server
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ -v --cov=src/other_agents_mcp --cov-report=term-missing

# Run specific test file
pytest tests/test_config.py -v

# Run MCP validation tests
pytest tests/mcp-validation/ -v
```

## 📊 Test Coverage & Validation

**MCP 검증 완료** ✅
- ✅ **79개 테스트 통과** (v2.1: +16 session tests)
- ✅ **전체 커버리지: 86.5%** (목표 80% 초과)
- ✅ **Session Manager: 95%** (16/16 통과)
- ✅ **Hit Rate: 100%** (목표 95% 초과)
- ✅ **Success Rate: 100%** (목표 99% 초과)
- ✅ **프로덕션 준비 완료**

**파일별 커버리지:**
- ✅ `__init__.py`: 100%
- ✅ `config.py`: 100%
- ✅ `session_manager.py`: 95% (NEW in v2.1)
- ✅ `logger.py`: 91.7%
- ✅ `server.py`: 88.1%
- ✅ `file_handler.py`: 85.7%
- ✅ `cli_manager.py`: 81.4%

**테스트 분류:**
- 프로토콜 테스트 (Phase 1): 17개
- 기능 테스트 (Phase 2): 28개
- E2E 테스트 (Phase 3): 18개
- **세션 테스트 (v2.1)**: 16개 ✨

## Architecture

```
MCP Client (Claude Code)
    ↓ stdio (JSON-RPC)
MCP Server (other_agents_mcp)
    ↓ File-based I/O
AI CLI (claude, gemini, codex, qwen)
```

자세한 내용은 다음 문서를 참조하세요:
- [**비동기 작업 실행 아키텍처 (Asynchronous Task Execution Architecture)**](./docs/ASYNC_TASK_ARCHITECTURE.md)

## 📚 Documentation

### Development Artifacts

Development artifacts (plans, reports, analysis) are stored locally in the `.artifacts/` directory to keep the repository clean.

- **`.artifacts/reports/`**: Final validation reports and summaries.
- **`.artifacts/plans/`**: Test and validation plans.
- **`.artifacts/analysis/`**: Code quality reviews and coverage analysis.

### Validation Reports

**프로덕션 배포 승인**: ✅ APPROVED

자세한 검증 과정 및 결과는 `tests/mcp-validation/` 디렉토리 참조:

- **`VALIDATION_REPORT.md`** - 최종 검증 보고서 (권장 읽기)
- `PROJECT_STATUS.md` - 전체 프로젝트 진행 상황
- `MCP_VALIDATION_PLAN.md` - 검증 계획 (5 phases)
- `PHASE0_SUCCESS_REPORT.md` - MCP SDK 설치 과정
- `PHASE1_COMPLETION_REPORT.md` - 서버 활성화 과정
- `PHASE3_COMPLETION_REPORT.md` - 행동 테스트 완료
- `MANUAL_TESTING_CHECKLIST.md` - MCP Inspector 수동 테스트 가이드
- `validation_metrics.json` - 메트릭 데이터

## ⚙️ Configuration

### 저장소 유형 (Storage Type)
`TaskManager`가 작업 상태를 저장하는 방식을 설정할 수 있습니다.

- **`memory` (기본값)**: 작업을 인-메모리에 저장합니다. 서버 재시작 시 모든 작업 내역이 사라집니다.
- **`sqlite`**: 작업을 SQLite 데이터베이스 파일(`.data/tasks.db`)에 영속적으로 저장합니다. 서버가 재시작되어도 작업 내역이 유지됩니다.

**설정 방법**:
`MCP_STORAGE_TYPE` 환경 변수를 사용하여 저장소 유형을 지정합니다.

```bash
# SQLite 저장소를 사용하려면 서버 실행 전 환경 변수를 설정합니다.
export MCP_STORAGE_TYPE=sqlite
python -m other_agents_mcp.server
```

## Usage

### As MCP Server

**Claude Code 설정** (`.claude/settings.local.json`):
```json
{
  "mcpServers": {
    "other-agents-mcp": {
      "command": "./venv/bin/python",
      "args": ["-m", "other_agents_mcp.server"]
    }
  }
}
```

**Claude Desktop 설정** (`~/.config/claude/mcp_servers.json`):
```json
{
  "other-agents-mcp": {
    "command": "/path/to/other-agents/venv/bin/python",
    "args": ["-m", "other_agents_mcp.server"],
    "cwd": "/path/to/other-agents"
  }
}
```

### Available Tools (MCP)

#### `list_agents`

서버에 설정된 CLI 도구 목록과 설치 상태를 반환합니다.

```json
{
  "name": "list_agents"
}
```

#### `use_agent`

AI CLI에 메시지를 보내고 응답이 올 때까지 대기하는 **동기(Synchronous)** 방식입니다. 간단하고 빠른 작업에 적합합니다.

**Stateless 모드 (기본)**:
```json
{
  "name": "use_agent",
  "arguments": {
    "cli_name": "claude",
    "message": "Write a hello world function"
  }
}
```

**Session 모드 (v2.1 NEW)** 🎉:
```json
{
  "name": "use_agent",
  "arguments": {
    "cli_name": "claude",
    "message": "파일 20~30번 분석해줘",
    "session_id": "analysis-001"
  }
}
```

**Session 이어가기**:
```json
{
  "name": "use_agent",
  "arguments": {
    "cli_name": "claude",
    "message": "25번 파일은 몇 번째였지?",
    "session_id": "analysis-001",
    "resume": true
  }
}
```

**비동기 모드 (Async Mode)**:
긴 작업에 권장되는 방식입니다. `run_async: true`를 설정하면 작업을 백그라운드에서 시작하고 즉시 `task_id`를 반환합니다.

```json
{
  "name": "use_agent",
  "arguments": {
    "cli_name": "claude",
    "message": "Write a python script that analyzes a large CSV file.",
    "run_async": true
  }
}
```

#### `get_task_status`

비동기 모드(`run_async=true`)로 시작된 작업의 상태를 조회합니다. 작업이 완료될 때까지 주기적으로 호출(polling)해야 합니다.

```json
{
  "name": "get_task_status",
  "arguments": {
    "task_id": "<your-task-id>"
  }
}
```

#### `add_agent`
런타임에 새로운 AI CLI 설정을 동적으로 추가합니다.

```json
{
  "name": "add_agent",
  "arguments": {
    "name": "my-custom-cli",
    "command": "my-cli-command"
  }
}
```

### Session Mode 사용 가이드

**Stateless vs Session 모드 선택**:

| 사용 케이스 | 모드 | session_id |
|-------------|------|------------|
| 간단한 일회성 질문 | Stateless | 없음 |
| 연속 분석/대화 | Session | 제공 |
| 여러 독립적 작업 | Stateless | 없음 |
| 컨텍스트 유지 필요 | Session | 제공 |

**세션 모드 예시**:
```python
# 첫 요청: 분석 시작
use_agent(cli_name="claude", message="프로젝트 분석", session_id="proj-a")

# 후속 요청: 이전 분석 재사용
use_agent(cli_name="claude", message="버그는?", session_id="proj-a", resume=True)

# 다른 세션: 동시 진행 가능
use_agent(cli_name="gemini", message="다른 작업", session_id="proj-b")
```

## License

MIT
