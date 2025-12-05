# AI CLI 시스템 프롬프트 주입 가이드

> **Last Updated:** 2025-12-01
> **Purpose:** Claude Code, Gemini CLI, Codex, Qwen Code의 시스템 프롬프트 커스터마이징 방법 참고 자료
> **Scope:** 검증된 사실만을 바탕으로 한 공식 문서 및 커뮤니티 가이드 종합

---

## 개요

본 문서는 other-agents 프로젝트에서 지원하는 4개 AI CLI 도구의 **시스템 프롬프트 주입 방법**을 조사하여 정리한 참고 자료입니다.

### 대상 독자
- AI CLI 도구 사용자
- 시스템 프롬프트 커스터마이징이 필요한 개발자
- 프로젝트별 컨텍스트 제공을 원하는 팀

### 조사 범위
- **대상 CLI**: Claude Code, Gemini CLI, OpenAI Codex, Qwen Code
- **조사 항목**: 명령줄 옵션, 환경변수, 설정 파일, 컨텍스트 파일
- **조사 방법**: 공식 문서, 검증된 커뮤니티 가이드

---

## CLI별 상세 가이드

### 1. Claude Code CLI

Claude Code는 시스템 프롬프트 커스터마이징을 위해 **명령줄 플래그**와 **CLAUDE.md 파일** 두 가지 방법을 제공합니다.

#### 1.1 명령줄 플래그

| 플래그 | 동작 방식 | 사용 모드 | 설명 |
|--------|----------|----------|------|
| `--system-prompt` | **완전 대체** | Interactive, Print | 기본 Claude Code 지침을 완전히 제거하고 사용자 프롬프트로 대체 |
| `--system-prompt-file` | **파일로 완전 대체** | Print only | 파일 내용으로 시스템 프롬프트를 대체 (버전 관리 용이) |
| `--append-system-prompt` | **추가** (권장) | Interactive, Print | 기본 Claude Code 기능을 유지하면서 사용자 지침 추가 |

**중요 제약사항:**
- `--system-prompt`와 `--system-prompt-file`은 **상호 배타적** (동시 사용 불가)
- `--append-system-prompt`는 **v1.0.51 이상**에서 사용 가능

**사용 예제:**

```bash
# 1. 완전 대체 (기본 지침 제거)
claude --system-prompt "You are a Python expert specializing in data science"

# 2. 파일로 완전 대체
claude -p --system-prompt-file ./prompts/custom-prompt.txt "Explain this code"

# 3. 추가 (권장 - 기본 기능 유지)
claude --append-system-prompt "Always use TypeScript with strict mode"

# 4. 복잡한 예제 (모델 + 추가 지침)
claude \
  --model claude-opus-4-1-20250805 \
  --append-system-prompt "Working in WSL2 environment. Use 'service' not 'systemctl'" \
  --add-dir ../shared-libraries \
  --max-tokens 8192
```

#### 1.2 CLAUDE.md 파일

Claude Code는 **계층적 컨텍스트 파일** 시스템을 지원합니다.

**위치:**
- **전역**: `~/.claude/CLAUDE.md` (모든 프로젝트에 적용)
- **프로젝트**: `<프로젝트>/.claude/CLAUDE.md` 또는 `<프로젝트>/CLAUDE.md`

**동작 방식:**
- Claude가 대화 시작 시 자동으로 컨텍스트에 포함
- 전역 → 프로젝트 순으로 로드 (프로젝트 설정이 우선)

**예제 CLAUDE.md:**
```markdown
# Project Context

## Technology Stack
- Python 3.11
- FastAPI
- PostgreSQL

## Coding Standards
- Use type hints for all function signatures
- Follow PEP 8 style guide
- Write docstrings in Google format

## Project-Specific Rules
- Database queries must use async SQLAlchemy
- API endpoints must include OpenAPI documentation
```

**권장 사항:**
- 일반적인 사용: `--append-system-prompt` 플래그 (기본 기능 유지)
- 팀 프로젝트: `CLAUDE.md` 파일 (버전 관리 가능)
- 완전한 제어: `--system-prompt` 또는 `--system-prompt-file`

**출처:**
- [CLI reference - Claude Code Docs](https://code.claude.com/docs/en/cli-reference)
- [The Complete Guide to Setting Global Instructions for Claude Code CLI](https://naqeebali-shamsi.medium.com/the-complete-guide-to-setting-global-instructions-for-claude-code-cli-cec8407c99a0)
- [Shipyard | Claude Code CLI Cheatsheet](https://shipyard.build/blog/claude-code-cheat-sheet/)

---

### 2. Gemini CLI

Gemini CLI는 **환경변수 기반 완전 대체** 또는 **컨텍스트 파일** 방식을 제공합니다.

#### 2.1 GEMINI_SYSTEM_MD 환경변수 (완전 대체)

**설정 방법:**

```bash
# 방법 1: .gemini/system.md 파일 사용
export GEMINI_SYSTEM_MD=true  # 또는 1
gemini

# 방법 2: 커스텀 경로 지정
export GEMINI_SYSTEM_MD="/absolute/path/to/custom-system.md"
gemini

# 방법 3: 세션별 설정
GEMINI_SYSTEM_MD=true gemini
```

**동작 방식:**
- **`true` 또는 `1`**: 프로젝트 루트의 `.gemini/system.md` 파일 사용
- **다른 문자열**: 해당 경로를 절대 경로로 해석하여 파일 로드
- 파일 내용이 기본 시스템 프롬프트를 **완전 대체** (추가가 아님)

**시각적 표시:**
- 커스텀 프롬프트가 활성화되면 CLI 하단에 **`|⌐■_■|` 아이콘** 표시

**⚠️ 중요 경고:**

Gemini CLI의 기본 시스템 프롬프트에는 **CLI 정상 작동에 필수적인 지침**이 포함되어 있습니다. 완전 대체 시 다음과 같은 문제가 발생할 수 있습니다:

- 파일 수정 기능 동작 불량
- 도구 호출(tool calling) 실패
- 컨텍스트 관리 오류

**사용 전 반드시** 기본 시스템 프롬프트를 확인하고 필수 지침을 포함해야 합니다.

**템플릿 생성 (GEMINI_SYSTEM_MD_WRITE):**

기본 시스템 프롬프트를 파일로 추출하여 템플릿으로 사용할 수 있습니다:

```bash
# .gemini/system.md에 기본 프롬프트 저장
export GEMINI_SYSTEM_MD_WRITE=true  # 또는 1
gemini

# 또는 커스텀 경로에 저장
export GEMINI_SYSTEM_MD_WRITE="/path/to/template.md"
gemini
```

이렇게 생성된 파일을 커스터마이징하여 사용할 수 있습니다.

**예제 .gemini/system.md (커스터마이징):**
```markdown
[기본 Gemini CLI 시스템 프롬프트 내용 - 필수 유지]

## Additional Project Context

This is a React TypeScript project with strict ESLint rules.

### Coding Standards:
- Use functional components with hooks
- Avoid class components
- Always define prop types with TypeScript interfaces
```

#### 2.2 GEMINI.md 컨텍스트 파일 (덜 침투적, 권장)

**위치 (계층적 로딩):**
1. **전역**: `~/.gemini/GEMINI.md` (사용자 홈 디렉토리, 모든 프로젝트 기본값)
2. **프로젝트 루트 및 상위 디렉토리**: 현재 작업 디렉토리에서 `.git` 폴더까지 검색
3. **하위 디렉토리**: 현재 디렉토리 아래의 모든 하위 디렉토리 검색 (`.gitignore`, `.geminiignore` 존중)

**동작 방식:**
- 시스템 프롬프트를 **대체하지 않고** 컨텍스트로 제공
- 기본 지침을 유지하면서 프로젝트별 정보 추가
- 모든 위치의 파일 내용을 **연결(concatenate)**하여 모델에 전달

**장점:**
- ✅ 기본 CLI 기능 보존
- ✅ 버전 관리 용이
- ✅ 팀 협업 시 일관성 유지
- ✅ 안전한 커스터마이징

**권장 사항:**
- **일반 사용자**: `GEMINI.md` 컨텍스트 파일 (기본 지침 유지)
- **고급 사용자**: `GEMINI_SYSTEM_MD` 환경변수 (완전 대체, 주의 필요)

**출처:**
- [Practical Gemini CLI: Bring your own system instruction](https://medium.com/google-cloud/practical-gemini-cli-bring-your-own-system-instruction-19ea7f07faa2)
- [Proactiveness considered harmful? A guide to customise the Gemini CLI](https://danicat.dev/posts/20250715-gemini-cli-system-prompt/)
- [Practical Gemini CLI: Instruction Following — System Prompts and Context](https://medium.com/google-cloud/practical-gemini-cli-instruction-following-system-prompts-and-context-d3c26bed51b6)

---

### 3. OpenAI Codex CLI

Codex CLI는 **파일 기반 컨텍스트**와 **재사용 가능한 커스텀 프롬프트**를 제공합니다.

#### 3.1 AGENTS.md 파일

**위치 (계층적 검색):**
1. **전역**: `~/.codex/AGENTS.md` (또는 `AGENTS.override.md`, `CODEX_HOME` 환경변수로 커스터마이징 가능)
2. **프로젝트 범위**: 저장소 루트에서 현재 작업 디렉토리까지 하향식 탐색
   - 각 디렉토리에서 다음 순서로 검색:
     1. `AGENTS.override.md` (최우선)
     2. `AGENTS.md`
     3. 설정된 대체 파일명 (`config.toml`의 `project_doc_fallback_filenames`)

**생성 방법:**
```bash
# Codex 실행
codex

# 프로젝트 초기화 (AGENTS.md 생성)
> /init
```

**동작 방식:**
- "파일은 루트에서 아래로 연결되며, **나중 파일이 먼저 파일을 재정의**합니다"
- 상위 디렉토리의 지침이 하위 디렉토리에서 덮어씌워짐
- 빈 파일은 무시됨

**AGENTS.override.md:**
- `AGENTS.md`보다 **우선순위가 높음**
- 같은 디렉토리에 두 파일이 있으면 `AGENTS.override.md`만 사용
- 일시적인 오버라이드나 테스트용으로 유용

**파일 크기 제한:**
- **기본값**: 32 KiB (32768 bytes)
- **최대 권장값**: 65536 bytes
- 설정 파일: `~/.codex/config.toml`
  ```toml
  project_doc_max_bytes = 65536
  ```
- 크기 제한 도달 시 검색 중단

**예제 AGENTS.md:**
```markdown
# Project Context for Codex

## Overview
This is a microservices architecture built with Node.js and TypeScript.

## Architecture
- API Gateway: Express.js
- Services: NestJS
- Database: MongoDB with Mongoose
- Message Queue: RabbitMQ

## Development Guidelines
- Use dependency injection
- Write unit tests with Jest
- API endpoints must follow RESTful conventions
- Error handling with custom exception filters
```

#### 3.2 커스텀 프롬프트 (재사용 가능한 프리셋)

**위치:**
- `~/.codex/prompts/` 디렉토리

**형식:**
- 마크다운 파일 (.md)

**동작 방식:**
- `~/.codex/prompts/` 디렉토리에 마크다운 파일 생성
- 파일명이 slash command가 됨 (예: `security-review.md` → `/prompts:security-review`)
- 메타데이터(description)를 포함하여 설명 추가 가능

**주요 내장 slash 명령어 (참고):**
- `/review`: 작업 트리의 변경사항 검토
- `/model`: 활성 모델 및 reasoning 레벨 선택
- `/init`: 현재 디렉토리에 AGENTS.md 생성
- `/diff`: untracked 파일 포함 git diff 표시
- `/mention`: 파일을 대화에 첨부
- `/status`: 세션 설정 및 토큰 사용량 표시

**참고:** `/prompts`는 내장 명령어가 아니며, 커스텀 프롬프트는 `/prompts:<name>` 형식으로 사용

**커스텀 프롬프트 생성 예제:**

`~/.codex/prompts/security-review.md`:
```markdown
---
description: Security-focused code review
---

# Security Code Review

Review the code for the following security concerns:

1. SQL injection vulnerabilities
2. XSS attack vectors
3. Authentication bypass possibilities
4. Sensitive data exposure
5. CSRF protection

Provide specific line numbers and remediation suggestions.
```

**사용:**
```bash
codex
> /prompts:security-review
```

#### 3.3 프롬프팅 원칙

**⚠️ 중요: 최소 프롬프트 권장**

GPT-5-Codex는 **코딩에 특화**되어 있어 다음과 같은 특징이 있습니다:

- ✅ 코딩 베스트 프랙티스가 이미 내장됨
- ✅ 최소한의 지침으로 높은 품질 달성
- ❌ 과도한 프롬프팅은 오히려 품질 저하

**비교:**
- Codex CLI 개발자 메시지: GPT-5 대비 **약 40% 적은 토큰** 사용
- 일반 모델에서 필요했던 많은 지침이 Codex에서는 불필요

**권장 사항:**
- **프로젝트별 컨텍스트**: `AGENTS.md` 파일 (`/init` 명령)
- **재사용 프리셋**: `~/.codex/prompts/` 커스텀 프롬프트
- **원칙**: 최소 프롬프트 (모델이 이미 코딩에 특화됨)

**출처:**
- [Codex CLI features](https://developers.openai.com/codex/cli/features/)
- [GPT-5-Codex Prompting Guide | OpenAI Cookbook](https://cookbook.openai.com/examples/gpt-5-codex_prompting_guide)
- [Plan Mode with the latest custom prompts capability in Codex CLI](https://github.com/openai/codex/discussions/4760)

---

### 4. Qwen Code CLI

Qwen Code는 **Gemini CLI에서 포크**되어 **계층적 컨텍스트 파일**과 **TOML 기반 커스텀 명령**을 제공합니다.

#### 4.1 QWEN.md 컨텍스트 파일 (계층적)

**위치 (계층적 로딩):**
1. **전역**: `~/.qwen/QWEN.md` (모든 프로젝트)
2. **프로젝트**: `<프로젝트>/QWEN.md` (해당 프로젝트)
3. **하위 디렉토리**: `<하위 디렉토리>/QWEN.md` (특정 디렉토리)

**생성 방법:**
```bash
qwen
> /init  # 현재 디렉토리 분석 후 QWEN.md 생성
```

**관리 명령:**
```bash
qwen

# 현재 로드된 모든 컨텍스트 파일 내용 표시
> /memory show

# 모든 위치에서 컨텍스트 파일 재로드
> /memory refresh
```

**동작 방식:**
- 계층적으로 모든 위치의 QWEN.md 파일을 로드
- 하위 디렉토리 설정이 상위를 오버라이드

**예제 QWEN.md:**
```markdown
# Qwen Code Project Context

## Project Type
Full-stack web application with Vue.js frontend and Django backend

## Technology Stack
- Frontend: Vue 3 + TypeScript + Vite
- Backend: Django 4.2 + Django REST Framework
- Database: PostgreSQL 15
- Cache: Redis

## Coding Standards
- Frontend: Composition API, script setup syntax
- Backend: Class-based views, type hints required
- Testing: pytest for backend, Vitest for frontend
```

#### 4.2 GEMINI.md 파일 (Gemini CLI 호환)

**배경:**
- Qwen Code는 Gemini CLI에서 포크되어 **Gemini CLI와 호환성 유지**

**위치:**
- 프로젝트 루트의 `GEMINI.md`

**동작:**
- `QWEN.md`와 동일하게 컨텍스트로 로드
- Gemini CLI 프로젝트를 Qwen Code에서도 사용 가능

#### 4.3 커스텀 명령 (재사용 가능한 프롬프트)

**위치:**
- **전역**: `~/.qwen/commands/` (모든 프로젝트에서 사용 가능)
- **프로젝트**: `<프로젝트>/.qwen/commands/` (해당 프로젝트만)

**형식:**
- TOML 파일

**TOML 파일 구조:**
```toml
description = "명령 설명 (한 줄)"
prompt = """
실행할 프롬프트 내용
여러 줄 가능
"""
```

**동적 치환 기능:**

| 구문 | 설명 | 예제 |
|-----|------|------|
| `{{args}}` | 사용자 입력 삽입 | `/cmd {{args}}` → 사용자가 입력한 텍스트 |
| `!{command}` | 셸 명령 실행 결과 주입 | `!{git branch --show-current}` |
| `@{path}` | 파일/디렉토리 내용 삽입 | `@{src/main.py}` |

**예제 1: 순수 함수 리팩토링** (`~/.qwen/commands/refactor/pure.toml`):
```toml
description = "순수 함수로 리팩토링"
prompt = """
다음 코드를 순수 함수(pure function)로 변환하세요.

요구사항:
1. 부작용(side effects) 제거
2. 동일한 입력에 항상 동일한 출력 반환
3. 외부 상태에 의존하지 않음

주요 변경사항을 설명하고 개선된 점을 나열하세요.
"""
```

**사용:**
```bash
qwen
> /refactor:pure @my-file.js
```

**예제 2: Git 커밋 메시지 생성** (`~/.qwen/commands/git/commit-msg.toml`):
```toml
description = "Git diff 기반 커밋 메시지 생성"
prompt = """
다음 Git diff를 분석하여 Conventional Commits 형식의 커밋 메시지를 작성하세요:

!{git diff --staged}

형식:
<type>(<scope>): <subject>

<body>

<footer>
"""
```

**사용:**
```bash
qwen
> /git:commit-msg
```

**예제 3: 프로젝트별 테스트 작성** (`<프로젝트>/.qwen/commands/test/write.toml`):
```toml
description = "pytest 테스트 코드 작성"
prompt = """
다음 코드에 대한 pytest 테스트를 작성하세요:

{{args}}

요구사항:
- pytest fixture 사용
- parametrize로 여러 케이스 테스트
- edge case 포함
- docstring 작성
"""
```

**사용:**
```bash
qwen
> /test:write @src/utils/parser.py
```

#### 4.4 settings.json 설정 파일

**위치:**
- `~/.qwen/settings.json`

**용도:**
- 영구 설정 저장 (환경변수, 모델 선택, 컨텍스트 파일명 등)

**context.fileName 커스터마이징:**

컨텍스트 파일명을 변경할 수 있습니다:

```json
{
  "context": {
    "fileName": "QWEN.md"
  }
}
```

또는 여러 파일을 지정:

```json
{
  "context": {
    "fileName": ["CONTEXT.md", "QWEN.md", "PROJECT.md"]
  }
}
```

**전체 settings.json 예제:**
```json
{
  "model": "qwen3-coder-plus",
  "temperature": 0.7,
  "max_tokens": 4096,
  "api_base": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
  "context": {
    "fileName": "QWEN.md"
  }
}
```

**권장 사항:**
- **프로젝트별 컨텍스트**: `QWEN.md` 또는 `GEMINI.md`
- **재사용 프리셋**: `~/.qwen/commands/` TOML 파일 (동적 치환 활용)
- **관리**: `/memory show`, `/memory refresh` 명령 활용

**출처:**
- [CLI Commands | Qwen Code](https://qwenlm.github.io/qwen-code-docs/en/cli/commands/)
- [Qwen Code CLI: A Guide With Examples | DataCamp](https://www.datacamp.com/tutorial/qwen-code)
- [Mastering Qwen Code CLI](https://medium.com/@innolyze/mastering-qwen-code-cli-your-essential-guide-to-efficient-command-line-coding-7e47e10667ee)

---

## 비교표

### 기능 비교

| CLI | 명령줄 플래그 | 환경변수 | 컨텍스트 파일 | 커스텀 명령/프리셋 | 동작 방식 |
|-----|-------------|---------|--------------|-------------------|----------|
| **Claude Code** | ✅ 3개<br>(완전 대체 2개, 추가 1개) | ❌ | ✅ CLAUDE.md<br>(계층적) | ❌ | 대체 또는 추가 |
| **Gemini CLI** | ❌ | ✅ GEMINI_SYSTEM_MD<br>(완전 대체) | ✅ GEMINI.md<br>(컨텍스트) | ❌ | 완전 대체 또는 컨텍스트 |
| **Codex** | ❌ | ❌ | ✅ AGENTS.md<br>(컨텍스트) | ✅ ~/.codex/prompts/<br>(마크다운) | 컨텍스트 추가 |
| **Qwen Code** | ❌ | ❌ | ✅ QWEN.md, GEMINI.md<br>(계층적) | ✅ ~/.qwen/commands/<br>(TOML) | 계층적 컨텍스트 |

### 플래그 상세 비교 (Claude Code)

| 플래그 | Interactive | Print | 대체/추가 | 권장 사용 |
|--------|-------------|-------|----------|----------|
| `--system-prompt` | ✅ | ✅ | 완전 대체 | 완전한 제어 필요 시 |
| `--system-prompt-file` | ❌ | ✅ | 완전 대체 | 버전 관리 + 재현성 |
| `--append-system-prompt` | ✅ | ✅ | 추가 (권장) | 일반 사용 |

### 파일 위치 비교

| CLI | 전역 위치 | 프로젝트 위치 | 계층적 로딩 |
|-----|----------|--------------|------------|
| **Claude Code** | `~/.claude/CLAUDE.md` | `<프로젝트>/.claude/CLAUDE.md`<br>`<프로젝트>/CLAUDE.md` | ✅ (전역 → 프로젝트) |
| **Gemini CLI** | `~/.gemini/GEMINI.md` | `<프로젝트>/GEMINI.md`<br>상위 디렉토리<br>하위 디렉토리 | ✅ (전역 → 상위 → 현재 → 하위) |
| **Codex** | `~/.codex/AGENTS.md`<br>`~/.codex/AGENTS.override.md` | `<저장소 루트>/AGENTS.md`<br>→ 현재 디렉토리까지 탐색<br>`AGENTS.override.md` (우선) | ✅ (전역 → 루트 → 하위) |
| **Qwen Code** | `~/.qwen/QWEN.md` | `<프로젝트>/QWEN.md`<br>`<하위 디렉토리>/QWEN.md` | ✅ (전역 → 프로젝트 → 하위) |

---

## 권장 사용 방법

### 사용 시나리오별 추천

#### 시나리오 1: 개인 프로젝트에서 간단한 지침 추가

**추천:**
- **Claude Code**: `--append-system-prompt "Use Python 3.11 syntax"`
- **Gemini CLI**: `GEMINI.md` 파일 생성
- **Codex**: `/init`로 `AGENTS.md` 생성
- **Qwen Code**: `/init`로 `QWEN.md` 생성

#### 시나리오 2: 팀 프로젝트에서 일관된 컨텍스트 공유

**추천:**
- **Claude Code**: `<프로젝트>/CLAUDE.md` (버전 관리)
- **Gemini CLI**: `<프로젝트>/GEMINI.md` (버전 관리)
- **Codex**: `<프로젝트>/AGENTS.md` (버전 관리)
- **Qwen Code**: `<프로젝트>/QWEN.md` (버전 관리)

#### 시나리오 3: 자주 사용하는 프롬프트 재사용

**추천:**
- **Claude Code**: 명령줄 alias 또는 스크립트 작성
- **Gemini CLI**: 명령줄 alias 또는 스크립트 작성
- **Codex**: `~/.codex/prompts/` 디렉토리에 마크다운 파일
- **Qwen Code**: `~/.qwen/commands/` 디렉토리에 TOML 파일

#### 시나리오 4: CI/CD 파이프라인에서 자동화

**추천:**
- **Claude Code**: `--system-prompt-file` + 버전 관리된 프롬프트 파일
- **Gemini CLI**: `GEMINI_SYSTEM_MD` 환경변수 + 파일 경로 지정
- **Codex**: `AGENTS.md` 파일 (저장소에 포함)
- **Qwen Code**: `QWEN.md` 파일 (저장소에 포함)

#### 시나리오 5: 완전한 제어가 필요한 경우 (실험적)

**추천:**
- **Claude Code**: `--system-prompt` (기본 지침 완전 제거)
- **Gemini CLI**: `GEMINI_SYSTEM_MD` (⚠️ 기본 지침 손실 주의)
- **Codex**: 적용 불가 (파일 기반만 지원)
- **Qwen Code**: 적용 불가 (파일 기반만 지원)

### CLI별 권장 워크플로우

#### Claude Code 권장 워크플로우

```bash
# 1. 전역 설정 (개인 선호도)
echo "- Always use type hints in Python" > ~/.claude/CLAUDE.md

# 2. 프로젝트별 설정
cat > ./CLAUDE.md <<EOF
# My Project

## Tech Stack
- FastAPI + SQLAlchemy
- PostgreSQL

## Rules
- Use async/await
- Write unit tests
EOF

# 3. 세션별 추가 지침
claude --append-system-prompt "Focus on security best practices"
```

#### Gemini CLI 권장 워크플로우

```bash
# 1. 프로젝트 컨텍스트 파일 (안전, 권장)
cat > ./GEMINI.md <<EOF
# React TypeScript Project

## Conventions
- Functional components only
- Hooks for state management
- Strict ESLint rules
EOF

gemini

# 2. 시스템 프롬프트 완전 대체 (고급, 주의)
mkdir -p .gemini
cat > .gemini/system.md <<EOF
[기본 Gemini CLI 시스템 프롬프트 - 필수 유지]

## Additional Instructions
- Always explain your reasoning
EOF

export GEMINI_SYSTEM_MD=true
gemini  # 하단에 |⌐■_■| 아이콘 확인
```

#### Codex 권장 워크플로우

```bash
# 1. 프로젝트 초기화
codex
> /init  # AGENTS.md 생성

# 2. 커스텀 프리셋 생성
mkdir -p ~/.codex/prompts/security
cat > ~/.codex/prompts/security/audit.md <<EOF
---
description: Security audit with OWASP focus
---

Perform a security audit focusing on OWASP Top 10:
1. Injection
2. Broken Authentication
3. Sensitive Data Exposure
...
EOF

# 3. 사용
codex
> /prompts:security/audit
```

#### Qwen Code 권장 워크플로우

```bash
# 1. 프로젝트 초기화
qwen
> /init  # QWEN.md 생성

# 2. 전역 커스텀 명령 (재사용 가능)
mkdir -p ~/.qwen/commands/doc
cat > ~/.qwen/commands/doc/generate.toml <<EOF
description = "Generate comprehensive documentation"
prompt = """
Analyze the following code and generate documentation:

{{args}}

Include:
1. Overview
2. Function signatures with type hints
3. Usage examples
4. Edge cases
"""
EOF

# 3. 사용
qwen
> /doc:generate @src/utils.py

# 4. 컨텍스트 확인
> /memory show
```

---

## 주의사항 및 베스트 프랙티스

### 공통 주의사항

1. **버전 관리**
   - ✅ DO: 컨텍스트 파일을 Git에 커밋하여 팀과 공유
   - ✅ DO: `.gitignore`에 개인 설정 파일 추가 (예: `~/.claude/CLAUDE.md`)
   - ❌ DON'T: API 키나 민감한 정보를 컨텍스트 파일에 포함

2. **프롬프트 길이**
   - ✅ DO: 간결하고 명확한 지침 작성
   - ❌ DON'T: 불필요하게 긴 프롬프트 (특히 Codex)

3. **계층 구조 이해**
   - ✅ DO: 전역 설정과 프로젝트 설정의 우선순위 이해
   - ✅ DO: 프로젝트별 설정으로 전역 설정 오버라이드

### CLI별 특이사항

#### Claude Code
- ⚠️ `--system-prompt`와 `--system-prompt-file` 동시 사용 불가
- ✅ `--append-system-prompt` 사용 권장 (기본 기능 유지)
- ✅ v1.0.51 이상 버전 확인

#### Gemini CLI
- ⚠️ `GEMINI_SYSTEM_MD` 사용 시 기본 지침 손실 주의
- ✅ **필수**: 기본 시스템 프롬프트를 포함하여 완전 대체
- ✅ 안전한 대안: `GEMINI.md` 컨텍스트 파일 사용
- ✅ `|⌐■_■|` 아이콘으로 커스텀 프롬프트 활성화 확인

#### Codex
- ✅ 최소 프롬프트 원칙 (모델이 이미 코딩에 특화)
- ❌ 과도한 지침은 품질 저하 초래
- ✅ `/init` 명령으로 `AGENTS.md` 자동 생성

#### Qwen Code
- ✅ 계층적 로딩 활용 (전역 → 프로젝트 → 하위)
- ✅ TOML 동적 치환 기능 적극 활용 (`{{args}}`, `!{cmd}`, `@{path}`)
- ✅ `/memory show`로 로드된 컨텍스트 확인
- ✅ Gemini CLI 호환성 유지 (`GEMINI.md` 사용 가능)

---

## 참고 자료

### Claude Code CLI
- [CLI reference - Claude Code Docs](https://code.claude.com/docs/en/cli-reference)
- [The Complete Guide to Setting Global Instructions for Claude Code CLI](https://naqeebali-shamsi.medium.com/the-complete-guide-to-setting-global-instructions-for-claude-code-cli-cec8407c99a0)
- [Shipyard | Claude Code CLI Cheatsheet](https://shipyard.build/blog/claude-code-cheat-sheet/)
- [CLAUDE.md: Best Practices Learned from Optimizing Claude Code with Prompt Learning](https://arize.com/blog/claude-md-best-practices-learned-from-optimizing-claude-code-with-prompt-learning/)
- [GitHub - awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code)
- [Replace system prompt in interactive mode for Claude Code · Issue #2692](https://github.com/anthropics/claude-code/issues/2692)

### Gemini CLI
- [Practical Gemini CLI: Bring your own system instruction](https://medium.com/google-cloud/practical-gemini-cli-bring-your-own-system-instruction-19ea7f07faa2)
- [Practical Gemini CLI: Instruction Following — System Prompts and Context](https://medium.com/google-cloud/practical-gemini-cli-instruction-following-system-prompts-and-context-d3c26bed51b6)
- [Proactiveness considered harmful? A guide to customise the Gemini CLI](https://danicat.dev/posts/20250715-gemini-cli-system-prompt/)
- [GitHub - google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli)
- [Google Gemini CLI Cheatsheet](https://www.philschmid.de/gemini-cli-cheatsheet)
- [Gemini CLI: Custom slash commands | Google Cloud Blog](https://cloud.google.com/blog/topics/developers-practitioners/gemini-cli-custom-slash-commands)

### OpenAI Codex CLI
- [Codex CLI features](https://developers.openai.com/codex/cli/features/)
- [Codex CLI reference](https://developers.openai.com/codex/cli/reference/)
- [GPT-5-Codex Prompting Guide | OpenAI Cookbook](https://cookbook.openai.com/examples/gpt-5-codex_prompting_guide)
- [Prompting guide](https://developers.openai.com/codex/prompting/)
- [Plan Mode with custom prompts · Discussion #4760](https://github.com/openai/codex/discussions/4760)
- [GitHub - feiskyer/codex-settings](https://github.com/feiskyer/codex-settings)

### Qwen Code CLI
- [CLI Commands | Qwen Code](https://qwenlm.github.io/qwen-code-docs/en/cli/commands/)
- [Qwen Code CLI |](https://qwenlm.github.io/qwen-code-docs/en/cli/index)
- [Qwen Code Configuration - zdoc](https://www.zdoc.app/en/QwenLM/qwen-code/blob/main/docs/cli/configuration.md)
- [Qwen Code CLI: A Guide With Examples | DataCamp](https://www.datacamp.com/tutorial/qwen-code)
- [Mastering Qwen Code CLI](https://medium.com/@innolyze/mastering-qwen-code-cli-your-essential-guide-to-efficient-command-line-coding-7e47e10667ee)
- [Qwen3-Coder: Agentic Coding in the World | Qwen](https://qwenlm.github.io/blog/qwen3-coder/)
- [GitHub - QwenLM/qwen-code](https://github.com/QwenLM/qwen-code)

---

## 버전 정보

- **Claude Code**: v1.0.51 이상 (--append-system-prompt 지원)
- **Gemini CLI**: 최신 버전 (2025년 기준)
- **Codex**: GPT-5-Codex 지원 (2025년 기준)
- **Qwen Code**: Qwen3-Coder 기반 (2025년 7월 출시)

---

## 업데이트 이력

| Date | Version | Changes |
|------|---------|---------|
| 2025-12-01 | 1.1.1 | Codex CLI 오류 수정<br>- `/plan` 명령어 제거 (존재하지 않는 명령어)<br>- `/prompts` 사용법 수정 → `/prompts:<name>` 형식으로 정정<br>- 실제 내장 slash 명령어 목록 추가 (/review, /model, /init, /diff, /mention, /status 등)<br>- 커스텀 프롬프트 동작 방식 명확화 |
| 2025-12-01 | 1.1.0 | 공식 문서 재조사 및 검증, 오류 수정<br>- Gemini CLI: GEMINI.md 전역 위치 추가, GEMINI_SYSTEM_MD_WRITE 추가<br>- Codex CLI: 전역 위치 추가, AGENTS.override.md 정보 추가, 파일 크기 제한 추가<br>- Qwen Code CLI: context.fileName 설정 예제 구체화<br>- 비교표 업데이트 (모든 CLI 계층적 로딩 반영) |
| 2025-12-01 | 1.0.0 | 초기 가이드 작성 (공식 문서 및 커뮤니티 가이드 기반) |

---

## 라이선스 및 면책조항

본 문서는 공식 문서 및 검증된 커뮤니티 가이드를 바탕으로 작성된 **참고 자료**입니다.

- ✅ 모든 정보는 2025년 12월 1일 기준으로 조사되었습니다.
- ⚠️ CLI 도구의 버전 업데이트에 따라 일부 내용이 변경될 수 있습니다.
- ✅ 실제 사용 전 각 CLI의 최신 공식 문서를 확인하시기 바랍니다.

**문서 작성자:** other-agents 프로젝트 팀
**문서 유지보수:** 프로젝트 기여자
