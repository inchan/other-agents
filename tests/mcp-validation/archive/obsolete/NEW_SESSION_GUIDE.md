# 새 세션 시작 가이드

**작성 일자**: 2025-11-30
**목적**: 컨텍스트 제한으로 인한 새 세션 시작 시 빠른 온보딩

---

## 🚀 빠른 시작 (1분)

새 세션에서 다음 명령어를 Claude에게 전달하세요:

```
다음 파일들을 읽고 프로젝트 상황을 파악해주세요:

1. tests/mcp-validation/SESSION_SUMMARY.md (전체 요약)
2. tests/mcp-validation/PROJECT_STATUS.md (현재 진행 상황)
3. tests/mcp-validation/MCP_VALIDATION_PLAN.md (검증 계획)

그리고 Phase 2를 계속 진행해주세요.
```

---

## 📋 상세 온보딩 (5분)

### 1단계: 프로젝트 개요 파악

**읽어야 할 핵심 문서** (우선순위 순):

```
1. tests/mcp-validation/SESSION_SUMMARY.md
   → 전체 작업 요약, 현재 상태, 다음 단계

2. tests/mcp-validation/PROJECT_STATUS.md
   → Phase별 진행률, 성공 기준, 메트릭

3. tests/mcp-validation/MCP_VALIDATION_PLAN.md
   → 4단계 검증 계획, 작업 항목
```

**Claude에게 요청**:
```
다음 3개 파일을 읽어주세요:
- tests/mcp-validation/SESSION_SUMMARY.md
- tests/mcp-validation/PROJECT_STATUS.md
- tests/mcp-validation/MCP_VALIDATION_PLAN.md

현재 프로젝트 상황을 요약해주세요.
```

---

### 2단계: 현재 환경 확인

**환경 정보**:
- **Python**: 3.12.12 (가상 환경: `venv/`)
- **MCP SDK**: 1.22.0
- **프로젝트 경로**: `/Users/chans/workspace/pilot/other-agents`
- **작업 공간**: `tests/mcp-validation/`

**가상 환경 활성화**:
```bash
cd /Users/chans/workspace/pilot/other-agents
source venv/bin/activate
```

**확인 명령어**:
```bash
# Python 버전
python --version

# MCP SDK 설치 확인
pip show mcp

# 서버 import 테스트
python -c "from other_agents_mcp.server import app; print('Server:', app.name)"

# 테스트 실행
pytest tests/mcp-validation/test_mcp_protocol.py -v
```

---

### 3단계: 현재 상태 이해

**완료된 Phase**:
- ✅ Phase 0: MCP SDK 설치 완료
- ✅ Phase 1: MCP 서버 활성화 완료
- 🔄 Phase 2: 기술 테스트 진행 중 (25%)

**Phase 2 진행 상황**:
- ✅ pytest 환경 설정
- ✅ 프로토콜 테스트 완료 (17/17 통과)
- ⬜ 도구 기능 테스트 (다음 작업)
- ⬜ 에러 핸들링 테스트
- ⬜ 비동기 처리 테스트

**현재 커버리지**: 55%
**목표 커버리지**: 80%

---

### 4단계: 다음 작업 파악

**즉시 실행 가능한 작업**:

#### Option A: Phase 2 계속 (권장)

**작업**: 도구 기능 테스트 작성

**Claude에게 요청**:
```
tests/mcp-validation/test_tools_functionality.py 파일을 생성해주세요.

다음 테스트를 포함해주세요:
1. list_available_clis 도구 기능 테스트
2. send_message 도구 기능 테스트
3. 파라미터 검증 테스트
4. Mock을 사용한 CLI 실행 테스트

test_mcp_protocol.py를 참고하여 작성해주세요.
```

---

#### Option B: MCP Inspector 수동 테스트

**작업**: Phase 1 수동 검증 완료

**Claude에게 요청**:
```
tests/mcp-validation/PHASE1_MANUAL_TEST_GUIDE.md를 읽고
MCP Inspector로 서버를 테스트하는 방법을 안내해주세요.
```

**실행 명령어**:
```bash
npx @modelcontextprotocol/inspector ./venv/bin/python -m other_agents_mcp.server
```

---

#### Option C: Phase 3 준비

**작업**: 행동 테스트 시나리오 정의

**Claude에게 요청**:
```
Phase 3 행동 테스트를 위한 시나리오 파일을 작성해주세요:
- tests/mcp-validation/test_scenarios.yaml
- 실제 사용 사례 기반 시나리오
```

---

## 🔧 문제 해결

### 문제: 파일을 찾을 수 없음

**확인**:
```bash
ls -la tests/mcp-validation/
```

**모든 문서 목록**:
- MCP_VALIDATION_TOOLS_RESEARCH.md
- MCP_VALIDATION_PLAN.md
- SELF_CRITICAL_REVIEW.md
- PHASE0_INSTALLATION_REPORT.md
- PHASE0_SUCCESS_REPORT.md
- PHASE1_MANUAL_TEST_GUIDE.md
- PHASE1_COMPLETION_REPORT.md
- PROJECT_STATUS.md
- SESSION_SUMMARY.md
- NEW_SESSION_GUIDE.md (본 문서)
- test_mcp_protocol.py

---

### 문제: 가상 환경이 활성화되지 않음

**해결**:
```bash
cd /Users/chans/workspace/pilot/other-agents
source venv/bin/activate

# 확인
which python
# 출력: /Users/chans/workspace/pilot/other-agents/venv/bin/python
```

---

### 문제: MCP SDK import 실패

**확인**:
```bash
pip show mcp
```

**재설치 (필요시)**:
```bash
pip install mcp>=0.9.0
```

---

## 📊 핵심 메트릭 요약

### 현재 상태

| 항목 | 값 |
|------|-----|
| 전체 진행률 | 40% (2/5 phases) |
| Phase 0 | 100% ✅ |
| Phase 1 | 100% ✅ |
| Phase 2 | 25% 🔄 |
| 테스트 통과 | 17/17 (100%) |
| 코드 커버리지 | 55% |
| 생성 문서 | 10개 |
| 총 작업 시간 | ~8시간 |

---

### 다음 목표

| 항목 | 목표 |
|------|------|
| Phase 2 완료 | 4개 테스트 파일 |
| 코드 커버리지 | 80% |
| 총 테스트 | 50+ |
| 예상 소요 시간 | 2-3일 |

---

## 🎯 추천 작업 순서

### 신규 세션 시작 시 (우선순위)

**1. 상황 파악** (5분)
```
Claude에게:
"다음 파일을 읽고 요약해주세요:
- tests/mcp-validation/SESSION_SUMMARY.md
- tests/mcp-validation/PROJECT_STATUS.md"
```

**2. 환경 확인** (2분)
```bash
source venv/bin/activate
pytest tests/mcp-validation/test_mcp_protocol.py -v
```

**3. 다음 작업 시작** (즉시)
```
Claude에게:
"test_tools_functionality.py를 작성해주세요.
test_mcp_protocol.py를 참고하여 작성해주세요."
```

---

## 💡 유용한 명령어

### 테스트 실행

```bash
# 전체 MCP 검증 테스트
pytest tests/mcp-validation/ -v

# 커버리지 포함
pytest tests/mcp-validation/ -v --cov=src/other_agents_mcp

# 특정 테스트 파일
pytest tests/mcp-validation/test_mcp_protocol.py -v

# 특정 테스트 클래스
pytest tests/mcp-validation/test_mcp_protocol.py::TestListToolsHandler -v

# 특정 테스트 함수
pytest tests/mcp-validation/test_mcp_protocol.py::TestListToolsHandler::test_list_tools_count -v
```

---

### MCP 서버 실행

```bash
# 직접 실행 (디버깅용)
python -m other_agents_mcp.server

# MCP Inspector로 실행 (테스트용)
npx @modelcontextprotocol/inspector ./venv/bin/python -m other_agents_mcp.server
```

---

### 문서 확인

```bash
# 모든 문서 목록
ls -la tests/mcp-validation/*.md

# 특정 문서 읽기
cat tests/mcp-validation/SESSION_SUMMARY.md

# 문서 검색
grep -r "Phase 2" tests/mcp-validation/
```

---

## 📝 Claude에게 전달할 컨텍스트

### 최소 컨텍스트 (빠른 시작)

```
프로젝트: AI CLI Ping-Pong MCP Server 검증

현재 상태:
- Phase 0 완료: MCP SDK 1.22.0 설치됨 (Python 3.12 + venv)
- Phase 1 완료: MCP 서버 활성화됨
- Phase 2 진행 중: 프로토콜 테스트 17개 통과 (55% 커버리지)

다음 작업: test_tools_functionality.py 작성

자세한 내용은 다음 파일 참조:
- tests/mcp-validation/SESSION_SUMMARY.md
- tests/mcp-validation/PROJECT_STATUS.md
```

---

### 전체 컨텍스트 (상세 이해 필요 시)

```
다음 파일들을 순서대로 읽고 프로젝트를 이해해주세요:

1. 전체 요약:
   - tests/mcp-validation/SESSION_SUMMARY.md

2. 현재 진행 상황:
   - tests/mcp-validation/PROJECT_STATUS.md

3. 검증 계획:
   - tests/mcp-validation/MCP_VALIDATION_PLAN.md

4. 각 Phase 보고서:
   - tests/mcp-validation/PHASE0_SUCCESS_REPORT.md
   - tests/mcp-validation/PHASE1_COMPLETION_REPORT.md

5. 기존 테스트 코드:
   - tests/mcp-validation/test_mcp_protocol.py

읽은 후, 현재 상황을 요약하고 다음 단계를 제안해주세요.
```

---

## ⚡ 빠른 재시작 템플릿

새 세션에서 Claude에게 다음을 복사해서 붙여넣으세요:

```
안녕하세요! 이전 세션에서 진행하던 MCP 검증 프로젝트를 계속하려고 합니다.

다음 3개 파일을 읽고 현재 상황을 파악해주세요:
1. tests/mcp-validation/SESSION_SUMMARY.md
2. tests/mcp-validation/PROJECT_STATUS.md
3. tests/mcp-validation/test_mcp_protocol.py (기존 테스트 참고)

그리고 다음 작업을 진행해주세요:
- tests/mcp-validation/test_tools_functionality.py 생성
- list_available_clis와 send_message 도구의 실제 동작 테스트
- Mock을 사용한 CLI 실행 테스트 포함
- 기존 test_mcp_protocol.py와 유사한 스타일로 작성

작업 공간: /Users/chans/workspace/pilot/other-agents
가상 환경: venv/ (Python 3.12.12)
```

---

## 🎓 중요 참고사항

### 1. 가상 환경 필수
모든 명령어는 가상 환경 활성화 후 실행:
```bash
source venv/bin/activate
```

### 2. 작업 디렉토리
주 작업 공간: `tests/mcp-validation/`

### 3. 문서 우선
코드 작성 전 관련 문서를 먼저 읽어야 합니다.

### 4. 테스트 먼저
새 기능 추가 시 테스트부터 작성 (TDD 방식).

---

## 📞 도움 받기

### 막힌 경우

**Claude에게 요청**:
```
tests/mcp-validation/ 디렉토리의 모든 .md 파일 목록을 보여주고,
각 파일의 목적을 간단히 설명해주세요.
```

### 진행 방향 불확실한 경우

**Claude에게 요청**:
```
PROJECT_STATUS.md를 읽고 현재 진행률과
다음에 해야 할 작업 3가지를 추천해주세요.
```

---

**가이드 버전**: 1.0
**최종 업데이트**: 2025-11-30
**다음 업데이트**: Phase 2 완료 시
