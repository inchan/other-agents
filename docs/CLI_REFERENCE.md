# AI CLI Reference

> **Last Updated:** 2025-12-15
> **Purpose:** 지원되는 AI CLI 도구들의 명령어, 설치 방법, 사용법 레퍼런스

---

## Supported CLI Tools

본 MCP 서버는 각 CLI 도구에 대해 **Headless**, **Yolo(Auto-approve)**, **Sandbox** 모드를 기본적으로 적용하여 안전하고 자동화된 실행 환경을 제공합니다.

| CLI | Command | NPM Package | Default Flags (MCP Server) |
|-----|---------|-------------|----------------------------|
| Claude Code | `claude` | `@anthropic-ai/claude-code` | `--print` (Headless), `--dangerously-skip-permissions` (Yolo), Native Sandbox |
| Gemini CLI | `gemini` | `@google/gemini-cli` | `--yolo`, `--sandbox` (Headless via pipe) |
| Codex CLI | `codex` | `@openai/codex` | `exec -`, `--full-auto` (Yolo), `--sandbox`, `--skip-git-repo-check` |
| Qwen Code | `qwen` | `@qwen-code/qwen-code` | `--headless`, `--yolo`, `--sandbox` |

---

## 1. Claude Code CLI

### Overview
Claude Code는 터미널에서 동작하는 agentic 코딩 도구로, 코드 읽기, 수정, 실행을 로컬에서 수행합니다. MCP 서버에서는 `--print` 플래그를 통해 비대화형(Headless)으로 실행되며, `--dangerously-skip-permissions`를 통해 사용자 개입 없이 동작합니다.

### Installation
```bash
npm install -g @anthropic-ai/claude-code
```

### Prerequisites
- Node.js 18 이상

### Available Models
- Sonnet 4.5 (기본)
- Opus 4.5
- Haiku 4.5

### References
- [Official GitHub](https://github.com/anthropics/claude-code)
- [Documentation](https://docs.claude.com/en/docs/claude-code/overview)

---

## 2. Gemini CLI

### Overview
Google의 오픈소스 AI 에이전트로, Gemini를 터미널에서 직접 사용할 수 있습니다. MCP 서버에서는 파이프 입력을 통해 자동으로 Headless 모드로 동작하며, `--yolo`와 `--sandbox` 플래그가 기본 적용됩니다.

### Installation
```bash
npm install -g @google/gemini-cli
```

### Prerequisites
- Google AI Studio API 키 또는 Vertex AI 키

### Available Models
- Gemini 2.5 Pro (기본, 1M context window)
- Gemini 3 Pro (Ultra 구독자용)

### References
- [Official GitHub](https://github.com/google-gemini/gemini-cli)
- [Documentation](https://developers.google.com/gemini-code-assist/docs/gemini-cli)

---

## 3. OpenAI Codex CLI

### Overview
OpenAI의 경량 코딩 에이전트입니다. MCP 서버에서는 `codex exec -` 명령을 사용하며, `--full-auto`(Yolo) 및 `--sandbox` 플래그가 적용됩니다.

### Installation
```bash
npm install -g @openai/codex
```

### Prerequisites
- ChatGPT Plus 이상 플랜

### Available Models
- GPT-5-Codex (기본)
- GPT-5

### References
- [Official GitHub](https://github.com/openai/codex)
- [Documentation](https://developers.openai.com/codex/cli/)

---

## 4. Qwen Code CLI

### Overview
Alibaba의 오픈소스 AI 코딩 도구입니다. MCP 서버에서는 `--headless`, `--yolo`, `--sandbox` 플래그를 명시적으로 사용하여 완전 자동화된 안전 모드로 실행됩니다.

### Installation
```bash
npm install -g @qwen-code/qwen-code
```

### Prerequisites
- Qwen API 키 또는 호환되는 OpenAI API 설정

### Available Models
- Qwen3-Coder-480B-A35B-Instruct (기본)

### References
- [Official Blog Post](https://qwenlm.github.io/blog/qwen3-coder/)
- [Community GitHub](https://github.com/dinoanderson/qwen_cli_coder)

---

## MCP Server Tools

본 MCP 서버는 AI CLI와의 상호작용을 표준화하고 추상화하는 여러 도구를 제공합니다. 특히 모든 도구 실행 시 **보안(Sandbox)**과 **자동화(Yolo/Headless)**가 기본 정책으로 적용됩니다.

### 1. `list_agents`
서버에 설정된 모든 AI CLI의 목록과 설치 상태, 버전 등의 정보를 조회합니다.

**Arguments**: 없음
**Returns**: `{"clis": [...]}`

### 2. `use_agent`
AI CLI에 프롬프트를 보내고 응답이 올 때까지 기다리는 도구입니다.

**기본 동작**:
- 모든 요청은 **Headless** 모드로 처리되어 대화형 프롬프트가 뜨지 않습니다.
- **Yolo** 모드가 활성화되어 권한 요청이 자동 승인됩니다.
- **Sandbox**가 적용되어 파일 시스템 접근이 제한되거나 안전하게 격리됩니다.

**Arguments**:
- `cli_name` (string, required): `list_agents`로 조회된 CLI 이름
- `message` (string, required): 전송할 프롬프트
- `system_prompt` (string, optional): 시스템 프롬프트
- `skip_git_repo_check` (boolean, optional): Git 저장소 체크 건너뛰기 (Codex 등 일부 CLI만 지원)
- `args` (array, optional): CLI에 전달할 추가 인자 (기본 플래그 외에 추가할 옵션)
- `timeout` (number, optional): 타임아웃 (초, 기본값: 1800)
- `run_async` (boolean, optional): 비동기 실행 여부

**Returns**:
- **동기 실행 (`run_async=false` 또는 생략)**: `{"response": "..."}`
- **비동기 실행 (`run_async=true`)**: `{"task_id": "...", "status": "running"}`

### 3. `use_agents`
여러 AI CLI에게 동시에 같은 질문을 보냅니다.

**Arguments**:
- `message` (string, required): 전송할 프롬프트
- `cli_names` (array, optional): 대상 CLI 목록 (생략 시 모든 CLI)
- `system_prompt` (string, optional): 시스템 프롬프트
- `timeout` (number, optional): 타임아웃 (초, 기본값: 1800)

**Returns**: `{"prompt": "...", "responses": {"claude": {...}, "gemini": {...}, ...}}`

### 4. `get_task_status`
비동기 작업의 상태를 조회합니다.

**Arguments**:
- `task_id` (string, required): 조회할 작업의 ID

**Returns**:
- `{"status": "running", "elapsed_time": ...}`
- `{"status": "completed", "result": "..."}`
- `{"status": "failed", "error": "..."}`

### 5. `add_agent`
런타임에 새로운 AI CLI 설정을 동적으로 추가합니다.

**Arguments**:
- `name` (string, required): CLI 이름
- `command` (string, required): 실행 명령어
- `extra_args` (array, optional): 기본으로 추가할 인자 (예: `["--headless", "--sandbox"]`)

---

## Update History

| Date | Version | Changes |
|------|---------|---------|
| 2025-12-15 | 1.2.0 | 기본 실행 모드(Headless, Yolo, Sandbox) 정책 적용 및 문서 업데이트 |
| 2025-12-03 | 1.1.0 | 비동기 작업 지원(`use_agent` with `run_async`, `get_task_status`) 추가 |
| 2025-11-30 | 1.0.0 | 초기 레퍼런스 작성 |
