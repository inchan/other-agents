# Other Agents MCP Server - Instructions

> **Project Status**: ✅ Production Ready
> **Last Updated**: 2025-11-30

---

## 프로젝트 개요

본 프로젝트는 로컬에 설치된 AI CLI 도구들(claude, gemini, codex, qwen)과 파일 기반으로 통신하는 **Model Context Protocol (MCP) 서버**입니다.

### 핵심 가치

- ✅ **통합**: 4개의 다양한 AI CLI를 하나의 인터페이스로 통합
- ✅ **확장성**: 3가지 방법으로 새로운 CLI 추가 가능 (런타임, 파일, 코드)
- ✅ **간단함**: stdin/stdout 파이프 방식으로 코드 단순화
- ✅ **안전성**: Stateless 설계로 세션 격리
- ✅ **신뢰성**: 110개 테스트 통과, 86% 코드 커버리지
- ✅ **프로덕션 준비**: 완전한 검증 및 배포 승인

---

## 주요 기능

### 1. list_agents
**설명**: 시스템에 설치된 AI CLI 목록 조회

**기능**:
- 자동 CLI 감지 (`shutil.which`)
- 버전 정보 조회 (`--version`)
- 설치 여부 확인

**사용 예시**:
```json
{
  "name": "list_agents"
}
```

**응답**:
```json
{
  "clis": [
    {
      "name": "claude",
      "command": "claude",
      "version": "1.0.0",
      "installed": true
    }
  ]
}
```

### 2. use_agent
**설명**: AI CLI에 메시지 전송 및 응답 수신

**기능**:
- 파일 기반 CLI 실행 (stdin/stdout 파이프)
- 임시 파일 자동 관리
- 환경 변수 지원
- Git 저장소 체크 스킵 (Codex)

**사용 예시**:
```json
{
  "name": "use_agent",
  "arguments": {
    "cli_name": "claude",
    "message": "Write a hello world function"
  }
}
```

**Codex 특수 옵션**:
```json
{
  "name": "use_agent",
  "arguments": {
    "cli_name": "codex",
    "message": "Write a hello world function",
    "skip_git_repo_check": true
  }
}
```

### 3. add_agent (NEW ✨)
**설명**: 런타임에 새로운 AI CLI 동적 추가

**기능**:
- 필수 필드만 요구 (name, command)
- 선택 필드 자동 기본값 적용
- 런타임 추가로 재시작 불필요 (테스트 및 임시 사용)

**최소 사용 예시**:
```json
{
  "name": "add_agent",
  "arguments": {
    "name": "deepseek",
    "command": "deepseek"
  }
}
```

**전체 옵션 예시**:
```json
{
  "name": "add_agent",
  "arguments": {
    "name": "custom_gpt",
    "command": "custom-gpt",
    "extra_args": ["--mode", "chat"],
    "timeout": 120,
    "env_vars": {"API_KEY": "your-key"},
    "supports_skip_git_check": false,
    "skip_git_check_position": "before_extra_args"
  }
}
```

**응답**:
```json
{
  "success": true,
  "message": "CLI 'deepseek' 추가 완료",
  "cli": {
    "name": "deepseek",
    "command": "deepseek"
  }
}
```

---

## 지원 CLI

### 기본 지원 (4개)

| CLI | Command | 환경 변수 | 특이사항 |
|-----|---------|----------|---------|
| **Claude Code** | `claude` | - | - |
| **Gemini CLI** | `gemini` | - | - |
| **OpenAI Codex** | `codex` | - | skip_git_check 지원 |
| **Qwen Code** | `qwen` | OPENAI_API_KEY 등 | 환경 변수 필요 |

### 커스텀 CLI 추가 (3가지 방법)

1. **런타임 추가** (`add_agent` 도구) - 재시작 불필요, 테스트용
2. **파일 기반** (`custom_clis.json`) - 프로젝트 공유 설정
3. **코드 추가** (`config.py`) - 공식 지원 CLI

**자세한 가이드**: [`docs/CLI_EXTENSION_GUIDE.md`](./CLI_EXTENSION_GUIDE.md)

---

## 설치 및 사용

### 빠른 시작

```bash
# 1. 가상 환경 생성
python3.12 -m venv venv
source venv/bin/activate

# 2. 패키지 설치
pip install -e .

# 3. 테스트 실행
pytest tests/ -v --cov

# 4. MCP 서버 실행
python -m other_agents_mcp.server
```

### 자세한 문서

- **[README.md](../README.md)** - 프로젝트 개요 및 설치 가이드
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - 시스템 아키텍처 및 구현 상세
- **[INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md)** - MCP 클라이언트 통합 방법
- **[CLI_REFERENCE.md](./CLI_REFERENCE.md)** - AI CLI 도구 레퍼런스
- **[REQUIREMENTS.md](./REQUIREMENTS.md)** - 요구사항 및 검증 결과

---

## 프로젝트 상태

### ✅ 구현 완료 (2025-11-30)

**구현된 기능**:
- MCP 프로토콜 완전 준수
- 2개 MCP 도구 (list_agents, use_agent)
- 4개 AI CLI 지원
- 환경 변수 지원
- Git 저장소 체크 스킵 (Codex)
- 3가지 커스텀 예외 처리
- 비동기 처리

### ✅ 검증 완료

**테스트 결과**:
- 63개 테스트 100% 통과
- 코드 커버리지: 86.5% (목표 80% 초과)
- Hit Rate: 100% (목표 95% 초과)
- Success Rate: 100% (목표 99% 초과)

**검증 범위**:
- 프로토콜 준수 (17개 테스트)
- 기능 정확성 (28개 테스트)
- E2E 시나리오 (18개 테스트)

### ✅ 프로덕션 준비 완료

**배포 승인**: ✅ **APPROVED FOR PRODUCTION**

**준비 사항**:
- 보안 검토 완료
- 성능 검증 완료
- 문서화 완료
- 메트릭 수집 완료

---

## 기술 스택

**언어 및 런타임**:
- Python 3.12.12 (최소 3.10+)

**핵심 의존성**:
- mcp 1.22.0 (Model Context Protocol SDK)

**개발 도구**:
- pytest 9.0.1 (테스트 프레임워크)
- pytest-cov 7.0.0 (코드 커버리지)
- pytest-asyncio 1.3.0 (비동기 테스트)
- black 24.11.0 (코드 포매터)
- ruff 0.8.5 (린터)

---

## 아키텍처 개요

```
MCP Client (Claude Code, Claude Desktop)
    ↓ stdio (JSON-RPC 2.0)
MCP Server (other_agents_mcp)
    ↓ File-based I/O (stdin/stdout pipe)
AI CLI (claude, gemini, codex, qwen)
```

**핵심 설계**:
- **Stateless**: 각 요청 독립적 처리
- **파일 기반**: stdin/stdout 파이프 방식
- **비동기**: asyncio.to_thread() 블로킹 방지
- **안전**: UUID 기반 임시 파일, 자동 정리

---

## 라이센스

MIT

---

## 참고 자료

### 프로젝트 문서
- [MCP Specification](https://modelcontextprotocol.io/specification/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector)

### 검증 보고서
- [`tests/mcp-validation/VALIDATION_REPORT.md`](../tests/mcp-validation/VALIDATION_REPORT.md) - 최종 검증 보고서
- [`tests/mcp-validation/PROJECT_STATUS.md`](../tests/mcp-validation/PROJECT_STATUS.md) - 프로젝트 진행 상황

---

**문서 버전**: 1.0
**작성일**: 2025-11-30
**프로젝트 상태**: ✅ Production Ready
