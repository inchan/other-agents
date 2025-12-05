# Other Agents MCP Server - Requirements

> **Status**: ✅ All Requirements Met + CLI Extensibility + Session Mode Added
> **Last Updated**: 2025-12-02 (v2.1)

---

## Version 2.1 New Features ✨

**FR-007**: 세션 모드 (Session Mode)
- Stateless/Session 모드 자동 전환 (session_id 유무로 판단)
- Session Manager 모듈 (세션 생명주기 관리)
- CLI별 세션 전략 (Claude: UUID, Gemini/Qwen: latest, Codex: last)
- 세션별 컨텍스트 유지 및 재개
- 다중 세션 격리 보장
- **Status**: ✅ Implemented (16/16 테스트 통과)

## Version 2.0 Features ✨

**FR-006**: 동적 CLI 확장 시스템
- `add_agent` MCP 도구 추가 (런타임 CLI 추가)
- CLI Registry 아키텍처 (3단계 병합)
- 파일 기반 설정 지원 (`custom_clis.json`)
- 필수/선택 필드 구분 (name, command 필수)
- **Status**: ✅ Implemented

---

## Functional Requirements

### Core Features (Implemented ✅)

**FR-001**: MCP 서버 구현
- MCP Protocol 준수 (JSON-RPC 2.0)
- stdio 서버 모드
- 3개 MCP 도구 제공 (v2.0: add_agent 추가)
- **Status**: ✅ Implemented

**FR-002**: CLI 목록 조회 (list_agents)
- 설치된 AI CLI 자동 감지 (`shutil.which`)
- 버전 정보 조회 (`--version`)
- CLIInfo 데이터 반환 (name, command, version, installed)
- 4개 CLI 지원: claude, gemini, codex, qwen
- **Status**: ✅ Implemented

**FR-003**: CLI 메시지 전송 (use_agent)
- 파일 기반 CLI 실행 (stdin/stdout 파이프)
- 임시 파일 자동 관리 (UUID 기반)
- 응답 반환
- **Status**: ✅ Implemented

**FR-004**: 환경 변수 지원
- CLI별 환경 변수 설정 (config.py의 `env_vars`)
- 시스템 환경 변수와 자동 병합 (`os.environ.copy()`)
- Qwen CLI용 OPENAI_BASE_URL, OPENAI_MODEL 지원
- **Status**: ✅ Implemented

**FR-005**: Git 저장소 체크 스킵
- Codex CLI의 `--skip-git-repo-check` 플래그 지원
- 옵션 파라미터로 제공 (skip_git_repo_check: bool)
- 플래그 위치 제어 (`skip_git_check_position`)
- **Status**: ✅ Implemented

---

## Non-Functional Requirements

### Performance (Verified ✅)

**NFR-001**: 응답 시간
- `list_agents`: <2초 **(실제: <1초)** ✅
- `use_agent` 에러 응답: <0.5초 **(실제: <0.5초)** ✅
- 동시 5개 요청 처리: <5초 **(실제: <5초)** ✅
- **Status**: ✅ Exceeded

**NFR-002**: Hit Rate
- 목표: ≥95%
- **실제: 100%** ✅
- **Status**: ✅ Exceeded (+5%)

**NFR-003**: Success Rate
- 목표: ≥99%
- **실제: 100%** ✅
- **Status**: ✅ Exceeded (+1%)

### Security (Implemented ✅)

**NFR-004**: 임시 파일 보안
- UUID 기반 파일명으로 충돌 방지
- `try-finally` 블록으로 자동 정리 보장
- `/tmp` 디렉토리 사용
- **Status**: ✅ Implemented

**NFR-005**: 명령어 인젝션 방지
- `subprocess.run()` 안전 사용
- 명령어를 리스트로 전달 (셸 미사용)
- 환경 변수 안전 병합
- **Status**: ✅ Implemented

### Reliability (Verified ✅)

**NFR-006**: 에러 처리
- 3가지 커스텀 예외 (CLINotFoundError, CLITimeoutError, CLIExecutionError)
- 에러 타입 명시 응답
- 타임아웃 설정 (기본 60초)
- **Status**: ✅ Implemented

**NFR-007**: 무상태 서버 (Stateless)
- 각 요청 독립적 처리
- 세션 없음
- UUID 기반 파일 격리
- **Status**: ✅ Implemented

**NFR-008**: 비동기 처리
- `asyncio.to_thread()`로 블로킹 방지
- MCP 핸들러 비동기 구현
- **Status**: ✅ Implemented

---

## Technical Requirements

### System Requirements (Verified ✅)

**TR-001**: Python 버전
- 최소: Python 3.10
- 권장: Python 3.12+
- **실제 사용: Python 3.12.12** ✅
- **Status**: ✅ Met

**TR-002**: 의존성
- `mcp >= 0.9.0`
- **실제 설치: mcp 1.22.0** ✅
- **Status**: ✅ Met

**TR-003**: 지원 CLI
- Claude Code (`claude`)
- Gemini CLI (`gemini`)
- OpenAI Codex (`codex`)
- Qwen Code (`qwen`)
- **Status**: ✅ All Supported

### Development Requirements (Met ✅)

**TR-004**: 테스트 커버리지
- 목표: ≥80%
- **실제: 86.5%** ✅
- **Status**: ✅ Exceeded (+6.5%)

**TR-005**: 테스트 통과율
- 목표: 100%
- **실제: 63/63 테스트 통과 (100%)** ✅
- **Status**: ✅ Perfect

**TR-006**: 문서화
- 아키텍처 문서
- 통합 가이드
- CLI 레퍼런스
- 검증 보고서
- **Status**: ✅ Complete

---

## User Requirements

### UR-001: 간단한 설치
- Python 가상 환경 사용
- `pip install -e .`로 설치
- **Status**: ✅ Met

### UR-002: 명확한 에러 메시지
- 에러 타입 명시
- 원인 설명
- **Status**: ✅ Met

### UR-003: 다양한 MCP 클라이언트 지원
- Claude Code ✅
- Claude Desktop ✅
- MCP Inspector ✅
- Custom Clients (MCP SDK) ✅
- **Status**: ✅ All Supported

---

## Constraints

### C-001: 파일 기반 통신
- **제약**: stdin/stdout 파이프 방식만 사용
- **이유**: 코드 단순화, 모든 CLI 통일 처리
- **Status**: ✅ Accepted

### C-002: Stateless 설계
- **제약**: 세션 없음, 매 요청 독립적
- **이유**: 보안, 안정성
- **Status**: ✅ Accepted

### C-003: Python 3.10+ 필수
- **제약**: MCP SDK 요구사항
- **해결**: Python 3.12 사용
- **Status**: ✅ Resolved

---

## Acceptance Criteria

**모든 기준 충족 ✅**

**AC-001**: MCP 프로토콜 준수
- JSON-RPC 2.0 프로토콜
- 도구 스키마 JSON Schema 준수
- **Status**: ✅ Verified (17개 프로토콜 테스트 통과)

**AC-002**: 63개 테스트 100% 통과
- 프로토콜 테스트: 17개
- 기능 테스트: 28개
- E2E 테스트: 18개
- **Status**: ✅ 100% Pass Rate

**AC-003**: 코드 커버리지 ≥80%
- 목표: 80%
- 실제: 86.5%
- **Status**: ✅ Exceeded

**AC-004**: Hit Rate ≥95%
- 목표: 95%
- 실제: 100%
- **Status**: ✅ Exceeded

**AC-005**: Success Rate ≥99%
- 목표: 99%
- 실제: 100%
- **Status**: ✅ Exceeded

**AC-006**: 프로덕션 배포 승인
- 보안 검토 ✅
- 성능 검증 ✅
- 문서화 완료 ✅
- **Status**: ✅ **APPROVED FOR PRODUCTION**

---

## Traceability Matrix

| Requirement ID | Implementation | Test Coverage | Status |
|---------------|----------------|---------------|--------|
| FR-001 | server.py:23 | test_mcp_protocol.py | ✅ Verified |
| FR-002 | cli_manager.py:81 | test_tools_functionality.py | ✅ Verified |
| FR-003 | file_handler.py:35 | test_tools_functionality.py | ✅ Verified |
| FR-004 | config.py:14, file_handler.py:150 | test_file_handler.py | ✅ Verified |
| FR-005 | file_handler.py:48, config.py:42 | test_file_handler.py | ✅ Verified |
| FR-006 | cli_registry.py, server.py:add_agent | test_cli_registry.py | ✅ Verified |
| FR-007 | session_manager.py, file_handler.py:336 | test_session_mode.py | ✅ Verified (16 tests) |
| NFR-001 | server.py:70 | test_e2e_scenarios.py | ✅ Verified |
| NFR-002 | collect_metrics.py | validation_metrics.json | ✅ Verified |
| NFR-003 | collect_metrics.py | validation_metrics.json | ✅ Verified |
| NFR-004 | file_handler.py:71-81, 211-219 | test_file_handler.py | ✅ Verified |
| NFR-005 | file_handler.py:181 | test_file_handler.py | ✅ Verified |
| NFR-006 | file_handler.py:20-32 | test_tools_functionality.py | ✅ Verified |
| NFR-007 | file_handler.py:71 (UUID) | test_e2e_scenarios.py | ✅ Verified |
| NFR-008 | server.py:70, 80 | test_mcp_protocol.py | ✅ Verified |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.1 | 2025-12-02 | Session Mode 추가 (FR-007) |
| 2.0 | 2025-11-30 | CLI 확장성 추가 (FR-006) |
| 1.0 | 2025-11-30 | Initial requirements documentation (post-implementation) |

---

**Document Status**: ✅ Complete
**Implementation Status**: ✅ 100% Complete
**Verification Status**: ✅ 100% Verified
**Production Status**: ✅ Approved
