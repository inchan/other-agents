# AI CLI Reference

> **Last Updated:** 2025-11-30
> **Purpose:** 지원되는 AI CLI 도구들의 명령어, 설치 방법, 사용법 레퍼런스

---

## Supported CLI Tools

| CLI | Command | NPM Package | Default Model | Status |
|-----|---------|-------------|---------------|--------|
| Claude Code | `claude` | `@anthropic-ai/claude-code` | Sonnet 4.5 | ✅ Active |
| Gemini CLI | `gemini` | `@google/gemini-cli` | Gemini 2.5 Pro | ✅ Active |
| Codex CLI | `codex` | `@openai/codex` | GPT-5-Codex | ✅ Active |
| Qwen Code | `qwen` | `@qwen-code/qwen-code` | Qwen3-Coder-480B | ✅ Active |

---

## 1. Claude Code CLI

### Overview
Claude Code는 터미널에서 동작하는 agentic 코딩 도구로, 코드 읽기, 수정, 실행을 로컬에서 수행합니다.

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

### File-Based Usage (추정)
```bash
# Input 파일에 프롬프트 작성
echo "Write a hello world function" > input.txt

# Claude 실행 (헤드리스 모드)
claude --headless --input input.txt --output output.txt

# Output 파일에서 결과 읽기
cat output.txt
```

### References
- [Official GitHub](https://github.com/anthropics/claude-code)
- [Documentation](https://docs.claude.com/en/docs/claude-code/overview)
- [Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)

---

## 2. Gemini CLI

### Overview
Google의 오픈소스 AI 에이전트로, Gemini를 터미널에서 직접 사용할 수 있습니다.

### Installation
```bash
npm install -g @google/gemini-cli
```

### Prerequisites
- Google AI Studio API 키 또는 Vertex AI 키

### Available Models
- Gemini 2.5 Pro (기본, 1M context window)
- Gemini 3 Pro (Ultra 구독자용)

### File-Based Usage (추정)
```bash
# Input 파일에 프롬프트 작성
echo "Write a hello world function" > input.txt

# Gemini 실행
gemini --headless --input input.txt --output output.txt

# Output 파일에서 결과 읽기
cat output.txt
```

### References
- [Official GitHub](https://github.com/google-gemini/gemini-cli)
- [Documentation](https://developers.google.com/gemini-code-assist/docs/gemini-cli)
- [Blog Announcement](https://blog.google/technology/developers/introducing-gemini-cli-open-source-ai-agent/)

---

## 3. OpenAI Codex CLI

### Overview
OpenAI의 경량 코딩 에이전트로, 최신 reasoning 모델을 터미널에서 사용할 수 있습니다.

### Installation
```bash
# npm 사용
npm i -g @openai/codex

# 또는 Homebrew (macOS)
brew install --cask codex
```

### Prerequisites
- ChatGPT Plus, Pro, Business, Edu, 또는 Enterprise 플랜

### Available Models
- GPT-5-Codex (기본)
- GPT-5

### File-Based Usage (추정)
```bash
# Input 파일에 프롬프트 작성
echo "Write a hello world function" > input.txt

# Codex 실행
codex --headless --input input.txt --output output.txt

# Output 파일에서 결과 읽기
cat output.txt
```

### References
- [Official GitHub](https://github.com/openai/codex)
- [Documentation](https://developers.openai.com/codex/cli/)
- [Getting Started Guide](https://help.openai.com/en/articles/11096431-openai-codex-cli-getting-started)

---

## 4. Qwen Code CLI

### Overview
Alibaba의 오픈소스 AI 코딩 도구로, Qwen3-Coder 모델을 사용합니다.

### Installation
```bash
npm install -g @qwen-code/qwen-code
```

### Prerequisites
- 환경 변수 설정 필요:
  - `OPENAI_API_KEY`: DashScope API 키
  - `OPENAI_BASE_URL`: https://dashscope-intl.aliyuncs.com/compatible-mode/v1
  - `OPENAI_MODEL`: qwen3-coder-plus

### Available Models
- Qwen3-Coder-480B-A35B-Instruct (기본, 256K-1M context)

### File-Based Usage (추정)
```bash
# 환경 변수 설정
export OPENAI_API_KEY="your-api-key"
export OPENAI_BASE_URL="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
export OPENAI_MODEL="qwen3-coder-plus"

# Input 파일에 프롬프트 작성
echo "Write a hello world function" > input.txt

# Qwen 실행
qwen --headless --input input.txt --output output.txt

# Output 파일에서 결과 읽기
cat output.txt
```

### References
- [Official Blog Post](https://qwenlm.github.io/blog/qwen3-coder/)
- [Community GitHub](https://github.com/dinoanderson/qwen_cli_coder)
- [Tutorial](https://www.datacamp.com/tutorial/qwen-code)

---

## Notes

### ⚠️ Important - MCP 서버 사용자 필독

본 문서의 **"File-Based Usage"** 섹션은 각 CLI의 실제 명령어를 **추정**한 것입니다.

**실제 MCP 서버 구현 방식**:

본 Other Agents MCP 서버는 파일 옵션 (--input/--output)을 사용하지 않고,
**stdin/stdout 파이프 방식**을 사용합니다:

```bash
cat input.txt | cli [args] > output.txt
```

**사용자는 CLI의 명령어 옵션을 직접 알 필요가 없습니다.**
MCP 도구(`use_agent`)를 통해 자동으로 처리됩니다.

**이 문서에서 정확한 정보**:
- ✅ CLI별 설치 가이드
- ✅ 지원 모델 정보
- ✅ 환경 변수 설정 (Qwen 등)

**추정 정보 (참고용)**:
- ⚠️ File-Based Usage 섹션 (실제 MCP 서버에서 사용하지 않음)

> **Last Updated:** 2025-12-03
> **Purpose:** 지원되는 AI CLI 도구들의 명령어, 설치 방법, 사용법 레퍼런스

---

## Supported CLI Tools

| CLI | Command | NPM Package | Default Model | Status |
|-----|---------|-------------|---------------|--------|
| Claude Code | `claude` | `@anthropic-ai/claude-code` | Sonnet 4.5 | ✅ Active |
| Gemini CLI | `gemini` | `@google/gemini-cli` | Gemini 2.5 Pro | ✅ Active |
| Codex CLI | `codex` | `@openai/codex` | GPT-5-Codex | ✅ Active |
| Qwen Code | `qwen` | `@qwen-code/qwen-code` | Qwen3-Coder-480B | ✅ Active |

---
... (Sections 1-4 remain unchanged) ...
---
## 4. Qwen Code CLI
...
### References
- [Official Blog Post](https://qwenlm.github.io/blog/qwen3-coder/)
- [Community GitHub](https://github.com/dinoanderson/qwen_cli_coder)
- [Tutorial](https://www.datacamp.com/tutorial/qwen-code)

---
## MCP Server Tools

본 MCP 서버는 AI CLI와의 상호작용을 표준화하고 추상화하는 여러 도구를 제공합니다.

### 1. `list_agents`
서버에 설정된 모든 AI CLI의 목록과 설치 상태, 버전 등의 정보를 조회합니다.

**Arguments**: 없음
**Returns**: `{"clis": [...]}`

### 2. `use_agent`
AI CLI에 프롬프트를 보내고 응답이 올 때까지 기다리는 **동기 방식** 도구입니다. 간단한 작업에 적합하지만, 긴 작업 시에는 클라이언트가 차단(blocking)될 수 있습니다.

**Arguments**:
- `cli_name` (string, required): `list_agents`로 조회된 CLI 이름
- `message` (string, required): 전송할 프롬프트
- `system_prompt` (string, optional): 시스템 프롬프트
- `skip_git_repo_check` (boolean, optional): Git 저장소 체크 건너뛰기 (Codex 등 일부 CLI만 지원)
- `args` (array, optional): CLI에 전달할 추가 인자
- `timeout` (number, optional): 타임아웃 (초, 기본값: 1800)

**Returns**:
- **동기 실행 (`run_async=false` 또는 생략)**: `{"response": "..."}`
- **비동기 실행 (`run_async=true`)**: `{"task_id": "...", "status": "running"}`

> **비동기 실행**: `run_async: true` 파라미터를 추가하면 긴 작업을 백그라운드에서 실행하고 즉시 `task_id`를 반환합니다. 이후 `get_task_status`로 상태를 조회할 수 있습니다.

### 3. `use_agents`
여러 AI CLI에게 동시에 같은 질문을 보내 다양한 관점의 답변을 받습니다.

**Arguments**:
- `message` (string, required): 전송할 프롬프트
- `cli_names` (array, optional): 대상 CLI 목록 (생략 시 모든 CLI)
- `system_prompt` (string, optional): 시스템 프롬프트
- `timeout` (number, optional): 타임아웃 (초, 기본값: 1800)

**Returns**: `{"prompt": "...", "responses": {"claude": {...}, "gemini": {...}, ...}}`

### 4. `get_task_status`
`use_agent(run_async=true)`로 시작된 비동기 작업의 현재 상태를 조회합니다.

**Arguments**:
- `task_id` (string, required): 조회할 작업의 ID

**Returns**:
- **작업 진행 중**: `{"status": "running", "elapsed_time": ...}`
- **작업 완료**: `{"status": "completed", "result": "..."}`
- **작업 실패**: `{"status": "failed", "error": "..."}`
- **작업 없음**: `{"status": "not_found", "error": "..."}`

### 5. `add_agent`
런타임에 새로운 AI CLI 설정을 동적으로 추가합니다.

**Arguments**:
- `name` (string, required): CLI 이름
- `command` (string, required): 실행 명령어
- ... (기타 설정 옵션)


### 비동기 작업 워크플로우 예시
긴 코드 생성 작업을 비동기적으로 처리하는 방법입니다.

1.  **작업 시작 (`use_agent` with `run_async: true`)**
    ```json
    {
      "name": "use_agent",
      "arguments": {
        "cli_name": "claude",
        "message": "Implement a class for a task management system in Python using SQLite for persistence.",
        "run_async": true
      }
    }
    ```
    서버는 즉시 다음과 같이 응답합니다:
    ```json
    {
      "task_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
      "status": "running"
    }
    ```

2.  **상태 확인 (`get_task_status`)**
    클라이언트는 `task_id`를 사용하여 작업이 끝날 때까지 주기적으로 상태를 확인(polling)합니다.
    ```json
    {
      "name": "get_task_status",
      "arguments": {
        "task_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef"
      }
    }
    ```
    작업이 아직 진행 중이라면 서버는 다음과 같이 응답합니다:
    ```json
    {
      "status": "running",
      "elapsed_time": 45.7
    }
    ```

3.  **결과 수신**
    작업이 완료되면, `get_task_status` 호출은 다음과 같은 최종 결과를 반환합니다.
    ```json
    {
      "status": "completed",
      "result": "class TaskManager:\n  # ... (생성된 코드) ..."
    }
    ```

---

## Update History

| Date | Version | Changes |
|------|---------|---------|
| 2025-12-03 | 1.1.0 | 비동기 작업 지원(`use_agent` with `run_async`, `get_task_status`) 추가 및 문서 개편 |
| 2025-11-30 | 1.0.0 | 초기 레퍼런스 작성 (웹 검색 기반) |
