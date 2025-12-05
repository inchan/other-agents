# CLI 확장 가이드

새로운 AI CLI를 추가하는 3가지 방법을 설명합니다.

---

## 방법 1: 런타임 추가 (add_agent 도구)

MCP 도구 `add_agent`를 사용하여 런타임에 CLI를 추가합니다.

### 사용 예시

```json
{
  "name": "add_agent",
  "arguments": {
    "name": "deepseek",
    "command": "deepseek"
  }
}
```

### 전체 옵션

```json
{
  "name": "add_agent",
  "arguments": {
    "name": "deepseek",
    "command": "deepseek",
    "extra_args": ["--mode", "chat"],
    "timeout": 120,
    "env_vars": {
      "API_KEY": "your-key"
    },
    "supports_skip_git_check": false,
    "skip_git_check_position": "before_extra_args"
  }
}
```

### 필수 필드

| 필드 | 설명 | 예시 |
|------|------|------|
| `name` | CLI 이름 (식별자) | `"deepseek"` |
| `command` | 실행 명령어 | `"deepseek"` |

### 선택 필드 (기본값)

| 필드 | 기본값 | 설명 |
|------|--------|------|
| `extra_args` | `[]` | 추가 명령줄 인자 |
| `timeout` | `60` | 타임아웃 (초) |
| `env_vars` | `{}` | 환경 변수 |
| `supports_skip_git_check` | `false` | Git 체크 스킵 지원 여부 |
| `skip_git_check_position` | `"before_extra_args"` | 플래그 위치 |

---

## 방법 2: 파일 기반 (custom_clis.json)

프로젝트 루트의 `custom_clis.json` 파일을 수정합니다.

### 파일 위치

```
other-agents/
├── custom_clis.json  ← 이 파일 수정
├── src/
└── docs/
```

### 예시

`custom_clis.json`:

```json
{
  "deepseek": {
    "command": "deepseek",
    "extra_args": [],
    "timeout": 60,
    "env_vars": {},
    "supports_skip_git_check": false,
    "skip_git_check_position": "before_extra_args"
  },
  "custom_gpt": {
    "command": "custom-gpt",
    "extra_args": ["--mode", "chat"],
    "timeout": 120,
    "env_vars": {
      "OPENAI_API_KEY": "your-api-key"
    },
    "supports_skip_git_check": false,
    "skip_git_check_position": "before_extra_args"
  }
}
```

### 최소 설정

```json
{
  "deepseek": {
    "command": "deepseek"
  }
}
```

---

## 방법 3: 기본 CLI 추가 (config.py)

공식 지원 CLI로 추가하려면 `src/other_agents_mcp/config.py`를 수정합니다.

### 파일 위치

```
src/other_agents_mcp/config.py
```

### 예시

```python
CLI_CONFIGS: dict[str, CLIConfig] = {
    "claude": { ... },
    "gemini": { ... },
    "codex": { ... },
    "qwen": { ... },
    "deepseek": {  # 새 CLI 추가
        "command": "deepseek",
        "extra_args": [],
        "timeout": 60,
        "env_vars": {},
        "supports_skip_git_check": False,
        "skip_git_check_position": "before_extra_args",
    }
}
```

---

## 병합 우선순위

3가지 방법으로 추가된 CLI는 다음 우선순위로 병합됩니다:

```
런타임 (add_agent) > 파일 (custom_clis.json) > 기본 (config.py)
```

**예시**: `deepseek`이 `config.py`와 `custom_clis.json`에 모두 있다면, `custom_clis.json`의 설정이 우선됩니다.

---

## 추가 후 확인

CLI를 추가한 후 `list_agents` 도구로 확인합니다:

```json
{
  "name": "list_agents"
}
```

**응답 예시**:

```json
{
  "clis": [
    {
      "name": "deepseek",
      "command": "deepseek",
      "version": "1.0.0",
      "installed": true
    }
  ]
}
```

---

## 추가한 CLI 사용

`use_agent` 도구로 추가한 CLI를 사용합니다:

```json
{
  "name": "use_agent",
  "arguments": {
    "cli_name": "deepseek",
    "message": "Write a hello world function"
  }
}
```

---

## 템플릿

### 최소 템플릿 (필수만)

```json
{
  "my_cli": {
    "command": "my-cli-command"
  }
}
```

### 전체 템플릿 (모든 옵션)

```json
{
  "my_cli": {
    "command": "my-cli-command",
    "extra_args": ["arg1", "arg2"],
    "timeout": 120,
    "env_vars": {
      "KEY1": "value1",
      "KEY2": "value2"
    },
    "supports_skip_git_check": false,
    "skip_git_check_position": "before_extra_args"
  }
}
```

---

## 방법 비교

| 방법 | 지속성 | 재시작 필요 | 용도 |
|------|--------|-------------|------|
| **add_agent** | 런타임만 | 재시작 시 사라짐 | 테스트, 임시 사용 |
| **custom_clis.json** | 영구 | 서버 재시작 | 프로젝트 공유 설정 |
| **config.py** | 영구 | 서버 재시작 | 공식 지원 CLI |

---

## 주의사항

1. **필수 필드**: `name`과 `command`는 반드시 제공해야 합니다.
2. **타임아웃**: 기본 60초. 긴 작업이 예상되면 늘려주세요.
3. **환경 변수**: API 키 등 민감한 정보는 MCP 환경변수나 `env_vars`로 전달하세요.
4. **Git 체크 스킵**: Codex처럼 특수한 경우가 아니면 `supports_skip_git_check: false`를 유지하세요.

---

**문서 버전**: 1.0
**작성일**: 2025-11-30
