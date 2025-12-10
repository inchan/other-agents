# Other Agents MCP Server - Architecture

> **Last Updated:** 2025-12-10
> **Status:** ✅ Implementation Complete, Production Ready

---

## Overview

로컬에 설치된 AI CLI 도구들(claude, gemini, codex, qwen)과 **파일 기반**으로 통신하는 MCP 서버입니다.

## Key Design Decisions

### 1. 파일 기반 통신 (Implemented)
- **방식**: stdin/stdout 파이프 (`cat input.txt | cli [args] > output.txt`)
- **입력**: 임시 파일(`input_<uuid>.txt`)에 프롬프트 작성
- **실행**: `subprocess.run()`으로 CLI 실행 (stdin=input_file, stdout=output_file)
- **출력**: 임시 파일(`output_<uuid>.txt`)에서 응답 읽기
- **정리**: `try-finally` 블록으로 자동 임시 파일 삭제
- **세션**: Stateless (매번 UUID 기반 새 파일 생성)

### 2. 통합 CLI 실행 방식 (Implemented)

**실제 구현**: stdin/stdout 파이프 방식만 사용

```
┌─────────────────────────────────┐
│  file_handler.py                │
│  - execute_cli_file_based()     │
│  - _execute_cli()               │
└──────────┬──────────────────────┘
           │
           ▼
   stdin/stdout 파이프 실행
   (모든 CLI 통일 방식)
           │
           ▼
cat input.txt | cli [extra_args] > output.txt
           │
    ┌──────┴──────┬──────┬──────┐
    │             │      │      │
    ▼             ▼      ▼      ▼
  claude       gemini  codex  qwen
```

**참고**: 초기 설계에서는 `file_mode` (direct/wrapped) 분기를 계획했으나,
실제 구현에서는 모든 CLI에 대해 stdin/stdout 방식을 사용하여 코드를 단순화했습니다.

### 3. 모듈 구조

```
src/other_agents_mcp/
├── __init__.py           # 패키지 초기화
├── config.py             # CLI 설정 (명령어, 옵션, 타임아웃)
├── cli_manager.py        # CLI 감지 및 버전 조회
├── file_handler.py       # 파일 I/O 추상화 (핵심)
└── server.py             # MCP 서버 및 도구 등록
```

---

## Module Details

### config.py

**역할**: CLI별 명령어 템플릿 및 설정 관리

**데이터 구조** (실제 구현):
```python
class CLIConfig(TypedDict):
    """CLI 설정 타입"""
    command: str
    timeout: int
    extra_args: list[str]
    env_vars: dict[str, str]  # 환경 변수 (✅ 구현 완료)
    supports_skip_git_check: bool  # --skip-git-repo-check 플래그 지원 (Codex)
    skip_git_check_position: str  # 플래그 위치: "before_extra_args" 또는 "after_extra_args"

CLI_CONFIGS: dict[str, CLIConfig] = {
    "claude": {
        "command": "claude",
        "extra_args": [],
        "timeout": 60,
        "env_vars": {},
        "supports_skip_git_check": False,
        "skip_git_check_position": "before_extra_args",
    },
    "gemini": {
        "command": "gemini",
        "extra_args": [],
        "timeout": 60,
        "env_vars": {},
        "supports_skip_git_check": False,
        "skip_git_check_position": "before_extra_args",
    },
    "codex": {
        "command": "codex",
        "extra_args": ["exec", "-"],
        "timeout": 60,
        "env_vars": {},
        "supports_skip_git_check": True,
        "skip_git_check_position": "after_extra_args",  # codex exec --skip-git-repo-check -
    },
    "qwen": {
        "command": "qwen",
        "extra_args": [],
        "timeout": 60,
        "env_vars": {
            "OPENAI_BASE_URL": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
            "OPENAI_MODEL": "qwen3-coder-plus",
        },
        "supports_skip_git_check": False,
        "skip_git_check_position": "before_extra_args",
    },
}
```

**의존성**: 없음

---

### cli_manager.py

**역할**: 시스템에 설치된 CLI 감지 및 정보 조회

**핵심 함수**:
```python
@dataclass
class CLIInfo:
    name: str
    command: str
    version: Optional[str]
    installed: bool

def list_agents() -> List[CLIInfo]:
    """설치된 CLI 목록 반환"""

def get_cli_version(command: str) -> Optional[str]:
    """CLI 버전 조회"""

def is_cli_installed(command: str) -> bool:
    """shutil.which()로 설치 여부 확인"""
```

**의존성**: config.py (CLI_CONFIGS 참조)

---

### file_handler.py

**역할**: 파일 I/O 추상화 - **핵심 모듈**

**핵심 함수** (실제 구현):
```python
import uuid
import tempfile
import subprocess
import os

def execute_cli_file_based(cli_name: str, message: str, skip_git_repo_check: bool = False) -> str:
    """
    파일 기반 CLI 실행

    Process:
    1. 임시 input 파일 생성 (tempfile.mkstemp(), prefix="other_agents_mcp_input_<uuid>_")
    2. CLI 실행 (stdin/stdout 파이프 방식)
       - cat input.txt | cli [extra_args] > output.txt
       - subprocess.run() 사용 (stdin=input_file, stdout=output_file)
    3. 임시 output 파일 읽기
    4. 임시 파일 정리 (try-finally 블록)

    Args:
        cli_name: CLI 이름 (claude, gemini, codex, qwen)
        message: 전송할 프롬프트
        skip_git_repo_check: Git 저장소 체크 건너뛰기 (Codex만 지원)

    Returns:
        CLI 응답 문자열

    Raises:
        CLINotFoundError: CLI가 설치되지 않음
        CLITimeoutError: 실행 타임아웃
        CLIExecutionError: 실행 중 에러 발생
    """

def _execute_cli(
    command: str,
    extra_args: list,
    env_vars: dict[str, str],
    input_path: str,
    output_path: str,
    timeout: int,
    skip_git_repo_check: bool = False,
    supports_skip_git_check: bool = False,
    skip_git_check_position: str = "before_extra_args"
) -> int:
    """
    CLI 실행 (환경 변수 설정 포함)

    - 환경 변수 병합 (os.environ.copy() + env_vars)
    - skip_git_check_position에 따라 플래그 위치 결정
    - stdin/stdout 파이프로 CLI 실행
    """

def _cleanup_temp_files(*file_paths: str) -> None:
    """임시 파일 정리 (에러 시에도 실행 보장)"""
```

**파일 명명 규칙**:
```
/tmp/other_agents_mcp_input_<uuid>.txt
/tmp/other_agents_mcp_output_<uuid>.txt
```

**의존성**: config.py (CLI_CONFIGS 참조)

---

### server.py

**역할**: MCP 서버 구현 및 도구 등록

**구조**:
```python
from mcp.server import Server
from mcp.server.stdio import stdio_server

app = Server("other-agents-mcp")

@app.list_agents()
async def list_agents():
    return [
        {
            "name": "list_agents",
            "description": "설치된 AI CLI 목록 조회",
            "inputSchema": {"type": "object", "properties": {}}
        },
        {
            "name": "use_agent",
            "description": "AI CLI에 메시지 전송 (파일 기반)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "cli_name": {"type": "string"},
                    "message": {"type": "string"}
                },
                "required": ["cli_name", "message"]
            }
        }
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Dict):
    if name == "list_agents":
        clis = list_agents()
        return {"clis": [cli.__dict__ for cli in clis]}
    elif name == "use_agent":
        response = execute_cli_file_based(
            arguments["cli_name"],
            arguments["message"]
        )
        return {"response": response}

if __name__ == "__main__":
    stdio_server(app)
```

**의존성**: cli_manager.py, file_handler.py

#### 연결 종료 에러 처리 (v0.0.5+)

MCP 클라이언트(Claude Desktop 등)가 연결을 조기 종료할 때 발생하는 에러를 graceful하게 처리합니다.

```python
def _is_connection_closed_error(exc: BaseException) -> bool:
    """연결 종료 에러인지 재귀적으로 확인 (중첩된 ExceptionGroup 지원)"""
    # 직접적인 연결 종료 에러
    if isinstance(exc, (BrokenPipeError, ConnectionResetError)):
        return True
    # ExceptionGroup으로 감싸진 경우 재귀 탐색
    if hasattr(exc, "exceptions"):
        return any(_is_connection_closed_error(e) for e in exc.exceptions)
    # __cause__ 체인 확인
    if exc.__cause__ is not None:
        return _is_connection_closed_error(exc.__cause__)
    return False
```

**처리되는 예외 유형**:
- `BrokenPipeError`: stdout 파이프 닫힘
- `ConnectionResetError`: 연결 리셋
- 중첩된 `ExceptionGroup` (Python 3.11+, anyio)
- `__cause__` 체인으로 연결된 예외

---

## Implementation History (Completed)

### ✅ Phase 0: MCP SDK 설치 (완료)
**실제 소요: 5시간** (Python 버전 문제 해결 포함)

- MCP SDK 1.22.0 설치
- Python 3.12 업그레이드
- 가상 환경 구축

### ✅ Phase 1: 기반 구조 (완료)
**실제 소요: 30분**

- 디렉토리 구조 생성
- config.py 작성 (실제로는 file_mode 미사용, stdin/stdout만 사용)
- 패키지 초기화

### ✅ Phase 2: 핵심 로직 (완료)
**실제 소요: 3시간** (병렬 작업)

**Track A: cli_manager.py** ✅
- CLIInfo 데이터클래스 정의
- CLI 감지 및 버전 조회 구현
- 테스트 작성 및 통과

**Track B: file_handler.py** ✅
- 파일 기반 CLI 실행 구현
- 3가지 커스텀 예외 정의
- 환경 변수 지원 추가
- skip_git_check 파라미터 구현
- 테스트 작성 및 통과

### ✅ Phase 3: MCP 통합 (완료)
**실제 소요: 2시간**

- server.py MCP 서버 구현
- 2개 MCP 도구 정의
- 비동기 처리 구현 (asyncio.to_thread)
- 통합 테스트 작성 및 통과

### ✅ Phase 4: 검증 및 문서화 (완료)
**실제 소요: 8시간**

- 63개 테스트 작성 (프로토콜 17 + 기능 28 + E2E 18)
- 100% 테스트 통과
- 86.5% 코드 커버리지 달성
- 검증 보고서 작성
- 프로덕션 배포 승인

---

## 자기비판 리뷰

### ✅ 강점
1. **사용자 요구사항 준수**: 파일 기반 통신을 명확히 구현
2. **추상화 설계**: file_handler.py가 다양한 CLI 인터페이스를 통합
3. **병렬 처리 최적화**: Phase 2에서 2개 트랙 동시 진행
4. **TDD 친화적**: 각 모듈이 독립적으로 테스트 가능
5. **Stateless**: 매번 새 파일 생성으로 세션 격리

### ⚠️ 잠재적 문제점

1. **CLI 인터페이스 불확실성**
   - **문제**: 각 CLI가 실제로 어떤 옵션을 지원하는지 미확인
   - **완화**: file_mode를 wrapped로 기본 설정, 테스트 단계에서 검증

2. **파일 I/O 오버헤드**
   - **문제**: 매번 디스크 읽기/쓰기로 성능 저하 가능
   - **완화**: 사용자가 "심플하고 간단하게" 요청, 성능보다 단순성 우선

3. **임시 파일 정리 실패**
   - **문제**: 예외 발생 시 임시 파일이 남을 수 있음
   - **완화**: try-finally 블록으로 보장, cleanup 함수 추가

4. **동시 요청 처리**
   - **문제**: 동시에 여러 요청 시 파일명 충돌 가능성
   - **완화**: UUID 사용으로 고유 파일명 생성

5. **타임아웃 설정**
   - **문제**: 각 CLI의 적절한 타임아웃 값 불명확
   - **완화**: 기본 60초 설정, config에서 수정 가능하게 구현

### ✅ 구현 완료된 기능

1. **환경 변수 지원** ✅
   - Qwen 등 CLI별 환경 변수 설정 지원 (config.py의 `env_vars`)
   - 시스템 환경 변수와 자동 병합 (`os.environ.copy()` + `env_vars`)

2. **Git 저장소 체크 스킵** ✅
   - Codex CLI의 `--skip-git-repo-check` 플래그 지원
   - `skip_git_check_position`으로 플래그 위치 제어

3. **로깅** ✅
   - 파일 생성/삭제 로그 (logger.py)
   - CLI 실행 명령어 로깅 (DEBUG 레벨)
   - stderr 스트림 핸들러

4. **에러 메시지** ✅
   - 3가지 커스텀 예외 타입 (CLINotFoundError, CLITimeoutError, CLIExecutionError)
   - 에러 타입 명시 응답
   - 명확한 에러 메시지

---

## Success Criteria

### Phase 1 ✅
- [x] pyproject.toml 존재
- [x] `from other_agents_mcp import __version__` 동작
- [x] `pytest` 실행 시 테스트 발견
- [x] `CLI_CONFIGS` 딕셔너리에 4개 CLI 정의

### Phase 2 (Track A) ✅
- [x] `list_agents()` 함수 존재
- [x] claude, gemini, codex는 installed=True
- [x] 각 CLI의 version 조회 (또는 None)
- [x] `pytest tests/test_cli_manager.py -v` 통과

### Phase 2 (Track B) ✅
- [x] `execute_cli_file_based("claude", "test")` 응답 반환
- [x] 임시 파일이 /tmp에 생성되었다가 삭제됨
- [x] stdin/stdout 파이프 방식 동작 (direct mode는 미구현)
- [x] timeout 시 CLITimeoutError 발생
- [x] `pytest tests/test_file_handler.py -v` 통과

### Phase 3 ✅
- [x] `python -m other_agents_mcp.server` 실행 가능
- [x] MCP 클라이언트 연결 성공
- [x] list_agents 도구 호출 시 JSON 응답
- [x] use_agent 도구 호출 시 실제 CLI 응답 반환
- [x] `pytest -v --cov` 전체 통과 (커버리지 86.5%, 목표 80% 초과)

---

## Next Steps

1. **환경 설정**
   ```bash
   cd /Users/chans/workspace/pilot/other-agents
   pip install -e ".[dev]"
   ```

2. **TDD 팀 시작**
   - Phase 1부터 순차적으로 진행
   - Phase 2는 Track A와 B 병렬 실행
   - 각 Phase마다 성공 기준 확인

3. **검증**
   - 실제 CLI 호출 테스트
   - MCP 클라이언트 연동 테스트

---

## Timeline (Actual)

| Phase | 병렬/순차 | 실제 소요 | 주요 작업 |
|-------|----------|----------|----------|
| Phase 0 | 순차 | 5시간 | MCP SDK 설치, Python 업그레이드 |
| Phase 1 | 순차 | 30분 | 기반 구조 생성 |
| Phase 2 | 병렬 (2트랙) | 3시간 | 핵심 로직 구현 |
| Phase 3 | 순차 | 2시간 | MCP 통합 |
| Phase 4 | 순차 | 8시간 | 검증 및 문서화 |
| **총계** | - | **18.5시간** | 프로덕션 배포 승인 ✅ |

---

## References

- [CLI_REFERENCE.md](./CLI_REFERENCE.md) - CLI 도구 레퍼런스
- [MCP Documentation](https://modelcontextprotocol.io/)
- [Python subprocess](https://docs.python.org/3/library/subprocess.html)
