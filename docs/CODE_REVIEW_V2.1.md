# 세션 모드 (v2.1) 코드 리뷰 보고서

> **리뷰 날짜**: 2025-12-02
> **리뷰어**: Claude Code Review Agent
> **리뷰 대상**: Session Mode Implementation (v2.1)

---

## 📊 리뷰 요약

| 항목 | 개수 |
|------|------|
| **전체 이슈** | 15개 |
| **Critical** | 4개 |
| **High/Important** | 4개 |
| **Medium/Low** | 7개 |
| **테스트 통과** | 16/16 (100%) |
| **커버리지** | 95% (session_manager.py) |

---

## 🚨 Critical Issues (즉시 수정 필요)

### 1. 세션 모드에서 timeout 파라미터 누락
**심각도**: Critical
**위치**: `file_handler.py:337-458`, `server.py:142-146`

**문제**:
- Stateless 모드는 timeout 지원하지만 Session 모드는 미지원
- 세션 모드에서 항상 기본 timeout(60초) 사용
- 긴 작업에 대한 timeout 조정 불가

**영향**:
- 기능 불일치
- 사용자 제어 불가

**수정 방안**:
```python
# file_handler.py:337
def execute_with_session(
    # ... 기존 파라미터
    timeout: int = None  # 추가
) -> str:
    # line 382
    execution_timeout = timeout if timeout is not None else config["timeout"]

    # line 440
    result = _execute_cli(
        timeout=execution_timeout,
        # ...
    )

# server.py:142
response = await asyncio.to_thread(
    execute_with_session,
    cli_name, message, session_id, resume,
    skip_git_repo_check, system_prompt, args,
    timeout  # 추가
)
```

---

### 2. 세션 ID 검증 부재로 인한 보안 취약점
**심각도**: Critical
**위치**: `session_manager.py:39-84`

**문제**:
- 세션 ID 검증 없음
- 세션 하이재킹 가능
- DoS 공격 가능 (무한 세션 생성)
- 메모리 누수

**영향**:
- 보안 취약점
- 서버 안정성 저하

**수정 방안**:
```python
import re

MAX_SESSION_ID_LENGTH = 128
SESSION_ID_PATTERN = re.compile(r'^[a-zA-Z0-9\-_]{8,128}$')

def create_or_get_session(self, session_id: str, cli_name: str) -> SessionInfo:
    # 세션 ID 검증
    if not session_id or len(session_id) > MAX_SESSION_ID_LENGTH:
        raise ValueError(f"Invalid session_id length: {len(session_id)}")

    if not SESSION_ID_PATTERN.match(session_id):
        raise ValueError(f"Invalid session_id format: {session_id}")

    # 세션 수 제한
    if session_id not in self._sessions and len(self._sessions) >= 1000:
        raise ValueError("Maximum session count reached")

    # ... 기존 로직
```

---

### 3. Codex 세션 모드 미구현
**심각도**: High
**위치**: `file_handler.py:499-507`

**문제**:
- TODO 상태로 완전히 미구현
- 경고 로그만 남기고 아무 작업 안 함
- 테스트 없음

**영향**:
- 기능 불완전
- Codex 세션 모드 작동 안 함

**수정 방안**:
```python
elif cli_name == "codex":
    if not is_first_request and resume:
        # 특수 마커 사용
        session_args.extend(["__CODEX_RESUME__", "--last"])
        logger.debug(f"Codex session resume: last")
    else:
        logger.debug(f"Codex new session (no flag)")

# _execute_cli에서 특수 처리
if cli_name == "codex" and "__CODEX_RESUME__" in additional_args:
    extra_args = ["resume"]
    additional_args = [arg for arg in additional_args if arg != "__CODEX_RESUME__"]
```

---

### 4. 세션 메모리 누수 가능성
**심각도**: High
**위치**: `session_manager.py:27-189`

**문제**:
- 세션 자동 정리 메커니즘 없음
- TTL 없음
- 최대 세션 수 제한 없음
- 장기 실행 시 메모리 증가

**영향**:
- 메모리 누수
- 서버 불안정

**수정 방안**:
```python
from datetime import datetime, timedelta

@dataclass
class SessionInfo:
    # ... 기존 필드
    ttl_minutes: int = 60

    def is_expired(self) -> bool:
        expiry_time = self.last_used + timedelta(minutes=self.ttl_minutes)
        return datetime.now() > expiry_time

class SessionManager:
    def __init__(self):
        self._sessions: Dict[str, SessionInfo] = {}
        self._max_sessions = 1000
        # 주기적 정리 스케줄러
        self._start_cleanup_scheduler()

    def _cleanup_expired_sessions(self):
        expired = [sid for sid, info in self._sessions.items() if info.is_expired()]
        for sid in expired:
            del self._sessions[sid]
            logger.info(f"Expired session cleaned up: {sid}")
```

---

## ⚠️ Important Issues (우선 수정 권장)

### 5. Claude 세션 ID UUID 검증 로직 불완전
**심각도**: Medium
**위치**: `session_manager.py:97-106`

**문제**:
- UUID가 아닌 경우 새로 생성하지만 클라이언트 ID와 불일치
- 세션 추적 실패 가능성

**수정 방안**:
```python
if cli_name == "claude":
    try:
        uuid.UUID(mcp_session_id)
        return mcp_session_id
    except ValueError:
        # 결정론적 UUID 생성
        logger.warning(f"Converting non-UUID to UUID: {mcp_session_id}")
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, mcp_session_id))
```

---

### 6. 인자 파싱 로직 복잡도 및 버그 위험
**심각도**: Medium
**위치**: `file_handler.py:268-323`

**문제**:
- `--flag value` 형식에서 value 판단 로직 불완전
- `--model --debug` 같은 경우 잘못 파싱 가능

**수정 필요**: 플래그-값 쌍 파싱 로직 개선

---

### 7. 테스트 코드의 실제 검증 부족
**심각도**: Medium
**위치**: `tests/test_session_mode.py:170-209`

**문제**:
- 모두 존재하지 않는 CLI로 에러만 테스트
- 실제 세션 생성/재개 테스트 없음

**수정 필요**: Mock을 사용한 통합 테스트 추가

---

### 8. 에러 처리 개선 필요
**심각도**: Medium
**위치**: `server.py:151-177`, `file_handler.py`

**문제**:
- 세션 관련 전용 에러 타입 없음
- 모든 에러가 `CLIExecutionError`로 처리

**수정 방안**:
```python
class SessionError(Exception):
    """세션 관련 에러"""
    pass

class SessionValidationError(SessionError):
    """세션 검증 에러"""
    pass
```

---

## 📝 Code Quality Issues

### 9. 코드 중복
**심각도**: Low
**위치**: `file_handler.py:38-152`, `337-458`

두 함수가 거의 동일한 로직 포함. 공통 함수 추출 권장.

---

### 10. 변수 네이밍 개선
**심각도**: Low
**위치**: `file_handler.py:93-95`, `403-405`

`session_id`가 함수 파라미터와 임시 파일 ID에 혼용됨.
→ `temp_file_id` 등으로 명확히 구분

---

### 11. 싱글톤 패턴 불일치
**심각도**: Low
**위치**: `session_manager.py:180-189`, `cli_registry.py:20-35`

SessionManager는 함수 기반, CLIRegistry는 `__new__` 기반.
→ 한 가지 패턴으로 통일 권장

---

### 12. 로깅 개선
**심각도**: Low
**위치**: 전체

로그 레벨 일관성 부족, 컨텍스트 정보 누락.

---

## 💡 추가 권장사항

### 13. 세션 모드 스키마에 timeout 추가
`server.py`의 `use_agent` inputSchema에 timeout 명시

### 14. 세션 통계 및 모니터링 개선
```python
def get_stats(self) -> dict:
    return {
        "total_sessions": len(self._sessions),
        "active_sessions": len(active_sessions),
        "expired_sessions": ...,
        "avg_requests_per_session": ...,
        "oldest_session_age_seconds": ...,
    }
```

### 15. 문서화 개선
- `execute_with_session` docstring 보강
- CLI별 플래그 매핑 표 추가
- 세션 모드 사용 예제 확대

---

## 🎯 수정 우선순위

| 우선순위 | 이슈 | 예상 작업 시간 |
|---------|------|--------------|
| **P0** | #1 timeout 파라미터 추가 | 30분 |
| **P0** | #2 세션 ID 검증 | 1시간 |
| **P0** | #3 Codex 세션 구현 | 1시간 |
| **P0** | #4 세션 메모리 관리 | 2시간 |
| **P1** | #5-8 Important 이슈들 | 2-3시간 |
| **P2** | #9-12 Code Quality | 1-2시간 |

**총 예상 작업 시간**: 7-10시간

---

## ✅ 잘된 점

1. **아키텍처 설계**
   - CLI별 세션 전략 명확히 분리
   - Stateless/Session 모드 자동 전환
   - 깔끔한 모듈 구조

2. **테스트 커버리지**
   - 16/16 테스트 통과 (100%)
   - SessionManager 95% 커버리지
   - 단위/통합 테스트 분리

3. **문서화**
   - README, REQUIREMENTS 업데이트 완료
   - 설계 문서 작성 (SESSION_MODE_DESIGN.md)
   - 사용 예시 제공

---

## 📋 액션 아이템

- [ ] Critical 이슈 4개 수정
- [ ] Important 이슈 4개 수정
- [ ] Code Quality 개선 (선택)
- [ ] 추가 통합 테스트 작성
- [ ] 문서 보강
- [ ] 전체 테스트 재실행 및 검증

---

**결론**: 세션 모드의 기본 구조는 견고하나, 보안(세션 ID 검증), 메모리 관리(세션 정리), 기능 완성도(Codex, timeout) 측면에서 개선 필요. Critical 이슈 해결 후 프로덕션 배포 권장.
