# Session Mode Design Document

## CLI 세션 기능 조사 결과

### 1. Claude CLI
**세션 지원**: ✅ **완벽 지원**

```bash
# 옵션 1: 마지막 대화 이어가기
claude --continue

# 옵션 2: 세션 ID로 재개
claude --resume <sessionId>
claude --resume  # 인터랙티브 선택

# 옵션 3: 특정 세션 ID 지정
claude --session-id <uuid>

# 옵션 4: 세션 포크 (새 ID로 복사)
claude --resume <sessionId> --fork-session
```

**특징**:
- `--session-id`: UUID 형식의 세션 ID 지정 가능
- `--resume`: 기존 세션 재개
- `--continue`: 가장 최근 세션 자동 재개
- `--fork-session`: 세션 복사 (새 ID 생성)

**우리 구현에 사용할 옵션**:
- `--session-id <uuid>`: 클라이언트가 제공한 session_id 사용
- `--resume <uuid>`: 기존 세션 이어가기

---

### 2. Gemini CLI
**세션 지원**: ✅ **지원**

```bash
# 옵션 1: 세션 재개 (인덱스 번호)
gemini --resume 5
gemini --resume latest  # 가장 최근

# 옵션 2: 세션 목록 조회
gemini --list-sessions

# 옵션 3: 세션 삭제
gemini --delete-session 5
```

**특징**:
- 프로젝트별 세션 관리
- 인덱스 기반 (숫자 또는 "latest")
- UUID 직접 지정 불가능 (인덱스만 가능)

**제약사항**:
- ❌ 커스텀 session_id 지정 불가
- ✅ 인덱스 기반만 지원

**우리 구현 방안**:
- Gemini는 "latest"만 사용 (가장 최근 세션 이어가기)
- 또는 session_id → 인덱스 매핑 테이블 필요

---

### 3. Codex CLI
**세션 지원**: ✅ **부분 지원**

```bash
# 옵션 1: 인터랙티브 세션 재개
codex resume

# 옵션 2: 마지막 세션 자동 재개
codex resume --last
```

**특징**:
- `codex resume`: 세션 선택 UI
- `codex resume --last`: 최근 세션 자동

**제약사항**:
- ❌ 특정 세션 ID 지정 불가
- ✅ `--last` 플래그만 가능

**우리 구현 방안**:
- Codex는 `--last` 사용 (최근 세션 이어가기)

---

### 4. Qwen CLI
**세션 지원**: ❓ **명시적 세션 옵션 없음**

Gemini CLI 기반으로 보이므로 유사할 가능성:
```bash
# Gemini와 동일한 옵션 예상
qwen --resume latest
```

**우리 구현 방안**:
- Gemini와 동일하게 처리
- 테스트 필요

---

## 세션 모드 구현 설계

### 아키텍처

```
MCP Client
    ↓
    use_agent({
        session_id: "user-defined-id",
        resume: true
    })
    ↓
MCP Server (other-agents)
    ↓
Session Manager
    ├─ session_id → CLI session mapping
    ├─ CLI별 세션 전략 적용
    └─ 세션 생명주기 관리
    ↓
CLI Execution
    ├─ Claude: --session-id <uuid> / --resume <uuid>
    ├─ Gemini: --resume latest
    ├─ Codex: codex resume --last
    └─ Qwen: --resume latest (추정)
```

---

## CLI별 세션 전략

| CLI | 전략 | 구현 방식 |
|-----|------|----------|
| **Claude** | UUID 기반 | `--session-id {session_id}` 또는 `--resume {session_id}` |
| **Gemini** | Latest 기반 | 첫 요청: 일반 실행, 후속 요청: `--resume latest` |
| **Codex** | Last 기반 | 첫 요청: 일반 실행, 후속 요청: `codex resume --last` |
| **Qwen** | Latest 기반 | Gemini와 동일 (추정) |

---

## 세션 매핑 구조

```python
# 서버 메모리에 저장
session_registry = {
    "user-session-001": {
        "cli_name": "claude",
        "cli_session_id": "uuid-abc-123",  # Claude용
        "created_at": "2025-12-02T10:00:00",
        "last_used": "2025-12-02T10:05:00",
        "request_count": 5
    },
    "user-session-002": {
        "cli_name": "gemini",
        "cli_session_id": "latest",  # Gemini는 latest만 사용
        "created_at": "2025-12-02T10:10:00",
        "last_used": "2025-12-02T10:12:00",
        "request_count": 3
    }
}
```

---

## 구현 우선순위

### Phase 1: Claude 세션 (P0)
- ✅ Claude는 완벽한 UUID 세션 지원
- ✅ 가장 간단하고 명확한 구현
- ✅ `--session-id` 플래그 직접 사용

### Phase 2: Gemini/Qwen 세션 (P1)
- `--resume latest` 사용
- 세션별 격리는 CLI가 담당

### Phase 3: Codex 세션 (P2)
- `codex resume --last` 사용
- 비대화형 모드 확인 필요

---

## 다음 단계

1. ✅ CLI 세션 기능 조사 완료
2. ⏭️ Session Manager 모듈 구현
3. ⏭️ Claude 세션 모드 구현 (Phase 1)
4. ⏭️ 테스트 작성 및 검증
5. ⏭️ Gemini/Codex 확장 (Phase 2/3)
