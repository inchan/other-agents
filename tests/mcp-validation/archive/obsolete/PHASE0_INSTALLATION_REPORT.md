# Phase 0: MCP SDK 설치 보고서

**실행 일자**: 2025-11-30
**작업자**: Claude Code
**상태**: ❌ 실패 (대안 필요)

---

## 📋 실행 요약

### 목표
MCP SDK (mcp>=0.9.0) 설치 확인 및 설치

### 결과
**실패**: Python 버전 호환성 문제

---

## 🔍 상세 실행 로그

### 시도 1: 버전 제약 조건 포함 설치
```bash
$ python3 -m pip install "mcp>=0.9.0"
```

**결과**:
```
ERROR: Could not find a version that satisfies the requirement mcp>=0.9.0 (from versions: none)
ERROR: No matching distribution found for mcp>=0.9.0
```

**문제**: pip 버전 오래됨 (21.2.4)

---

### 시도 2: pip 업그레이드
```bash
$ python3 -m pip install --upgrade pip --user
```

**결과**:
```
Successfully installed pip-25.3
```

**상태**: ✅ 성공

---

### 시도 3: MCP SDK 재설치 시도
```bash
$ python3 -m pip install mcp
```

**결과**:
```
ERROR: Ignored the following versions that require a different python version:
  0.9.1 Requires-Python >=3.10
  1.0.0 Requires-Python >=3.10
  ...
  1.22.0 Requires-Python >=3.10
ERROR: Could not find a version that satisfies the requirement mcp (from versions: none)
ERROR: No matching distribution found for mcp
```

**근본 원인 발견**: MCP SDK는 Python 3.10+ 필요

---

### 시도 4: 현재 Python 버전 확인
```bash
$ python3 --version
```

**결과**:
```
Python 3.9.6
```

**문제**: 현재 시스템 Python 3.9.6 (MCP SDK 요구사항 미충족)

---

### 시도 5: Python 3.10+ 설치 여부 확인
```bash
$ which python3.10 python3.11 python3.12
```

**결과**:
```
python3.10 not found
python3.11 not found
python3.12 not found
No Python 3.10+ found
```

**상태**: ❌ Python 3.10+ 미설치

---

## ❌ 발견된 문제

### Critical Issue 1: Python 버전 불일치

**문제 설명**:
- **프로젝트 요구사항** (`pyproject.toml`): `requires-python = ">=3.9"`
- **MCP SDK 요구사항** (PyPI): `Requires-Python >=3.10`
- **현재 시스템**: Python 3.9.6

**영향**:
- MCP SDK 설치 불가능
- Phase 1-4 실행 불가능
- 전체 검증 계획 중단 위험

**심각도**: **Critical**

---

### Critical Issue 2: pyproject.toml 정보 불일치

**문제 설명**:
`pyproject.toml` 파일의 Python 버전 요구사항이 실제 의존성과 불일치

**현재 상태**:
```toml
[project]
requires-python = ">=3.9"
dependencies = [
    "mcp>=0.9.0",  # 실제로는 Python 3.10+ 필요
]
```

**올바른 상태**:
```toml
[project]
requires-python = ">=3.10"  # MCP SDK 요구사항에 맞춤
dependencies = [
    "mcp>=0.9.0",
]
```

**영향**:
- 개발 환경 설정 시 혼란
- CI/CD 파이프라인 실패 가능성

---

## 🔄 대안 (Options)

### Option A: Python 3.10+ 설치 (권장)

**방법**:
```bash
# Homebrew 사용 (macOS)
brew install python@3.10

# 또는 최신 버전
brew install python@3.12

# 설치 후 확인
python3.10 --version
python3.12 --version
```

**장점**:
- ✅ 공식 MCP SDK 사용 가능
- ✅ 최신 기능 및 버그 수정 포함
- ✅ 장기적으로 안정적

**단점**:
- ⚠️ 시스템 Python 변경 필요
- ⚠️ 다른 프로젝트 영향 가능성

**추정 시간**: 30분 - 1시간

**우선순위**: ⭐⭐⭐⭐⭐ (최우선)

---

### Option B: 가상 환경에서 Python 3.10+ 사용

**방법**:
```bash
# pyenv 설치 (macOS)
brew install pyenv

# Python 3.12 설치
pyenv install 3.12

# 프로젝트 디렉토리에서 Python 버전 설정
cd /Users/chans/workspace/pilot/other-agents
pyenv local 3.12

# 가상 환경 생성
python3 -m venv venv
source venv/bin/activate

# MCP SDK 설치
pip install mcp>=0.9.0
```

**장점**:
- ✅ 시스템 Python 영향 없음
- ✅ 프로젝트별 격리된 환경
- ✅ 재현 가능한 환경

**단점**:
- ⚠️ pyenv 설치 필요
- ⚠️ 환경 관리 복잡도 증가

**추정 시간**: 1-2시간

**우선순위**: ⭐⭐⭐⭐ (권장)

---

### Option C: MCP 프로토콜 수동 구현

**방법**:
- MCP 프로토콜 스펙 직접 구현
- JSON-RPC 2.0 기반 통신
- stdio 전송 계층 직접 구현

**장점**:
- ✅ Python 버전 제약 없음
- ✅ 의존성 최소화
- ✅ 학습 효과

**단점**:
- ❌ 구현 시간 많이 소요 (1-2주)
- ❌ 버그 및 호환성 문제 위험
- ❌ 공식 업데이트 미반영

**추정 시간**: 1-2주

**우선순위**: ⭐ (최후의 수단)

---

### Option D: 대체 라이브러리 사용 (FastMCP)

**방법**:
```bash
# FastMCP 설치 시도
python3 -m pip install fastmcp
```

**조사 필요**:
- FastMCP의 Python 버전 요구사항 확인
- MCP 표준 스펙 준수 여부 확인
- 프로덕션 준비 상태 확인

**장점**:
- ✅ 더 쉬운 API (가능성)
- ✅ Python 3.9 지원 가능성

**단점**:
- ⚠️ 비공식 라이브러리
- ⚠️ 호환성 불확실

**추정 시간**: 2-4시간 (조사 + 테스트)

**우선순위**: ⭐⭐⭐ (조사 가치 있음)

---

## ✅ 권장 조치 (Action Plan)

### 즉시 실행 (오늘)

**1단계: FastMCP 조사** (30분)
```bash
# FastMCP 설치 가능 여부 확인
python3 -m pip install fastmcp

# 버전 및 호환성 확인
python3 -c "import fastmcp; print(fastmcp.__version__)"
```

**결과에 따른 분기**:
- ✅ 성공 → FastMCP로 진행 (Phase 1 시작)
- ❌ 실패 → 2단계로

---

**2단계: Python 3.10+ 설치 결정** (1-2시간)

**Option A 선택 시** (시스템 전체 업그레이드):
```bash
# Homebrew로 Python 3.12 설치
brew install python@3.12

# 심볼릭 링크 생성 (선택)
ln -s /opt/homebrew/bin/python3.12 /usr/local/bin/python3

# 프로젝트에서 테스트
cd /Users/chans/workspace/pilot/other-agents
python3 -m pip install mcp>=0.9.0
```

**Option B 선택 시** (가상 환경):
```bash
# pyenv + venv 조합
brew install pyenv
pyenv install 3.12
cd /Users/chans/workspace/pilot/other-agents
pyenv local 3.12
python3 -m venv venv
source venv/bin/activate
pip install mcp>=0.9.0
```

---

**3단계: pyproject.toml 수정** (5분)
```toml
[project]
requires-python = ">=3.10"  # 3.9에서 3.10으로 변경
dependencies = [
    "mcp>=0.9.0",
]
```

---

### 단기 조치 (내일)

**Phase 1 재시작**:
- MCP SDK 정상 설치 확인
- `server.py` 주석 해제
- 기본 검증 실행

---

## 📊 영향 분석

### 일정 영향

**원래 계획**:
```
Phase 0: 0.5일 (MCP SDK 설치)
Phase 1: 1-2일
...
```

**수정된 계획**:
```
Phase 0: 1-2일 (Python 업그레이드 + MCP SDK 설치)
  - 0.5일: FastMCP 조사
  - 0.5-1일: Python 3.10+ 설치
  - 0.5일: MCP SDK 설치 및 검증
Phase 1: 1-2일
...
```

**총 지연**: +0.5-1.5일

---

### 리스크 업데이트

| 리스크 | 이전 평가 | 현재 평가 | 변경 사유 |
|--------|-----------|-----------|----------|
| MCP SDK 호환성 | 중/높음 | **Critical/Critical** | Python 버전 불일치 확인 |
| 일정 지연 | 낮음/중 | 중/중 | +1-2일 추가 소요 |

---

## 📝 학습 사항 (Lessons Learned)

### 1. 의존성 검증의 중요성
**교훈**: 프로젝트 초기 단계에서 모든 의존성의 **실제 요구사항**을 검증해야 함

**개선**:
- pyproject.toml 작성 시 의존성의 Python 버전 요구사항 확인
- CI/CD에서 여러 Python 버전 테스트

---

### 2. Phase 0의 필요성 검증
**교훈**: 자기비판 리뷰에서 제안한 "Phase 0 추가"가 정확한 판단이었음

**증거**:
- Phase 0 없이 Phase 1부터 시작했다면 더 큰 지연 발생
- 조기 발견으로 대응 시간 확보

---

### 3. 대안 준비의 중요성
**교훈**: 단일 경로에 의존하지 않고 여러 대안 준비 필요

**적용**:
- Option A-D까지 4가지 대안 수립
- 각 대안의 장단점 및 우선순위 평가

---

## 🎯 다음 단계

### 즉시 (30분 내)
- [ ] FastMCP 설치 가능 여부 확인
- [ ] FastMCP로 진행 가능 시 Phase 1 시작

### 단기 (오늘 내)
- [ ] Python 3.10+ 설치 방법 결정 (Option A or B)
- [ ] 설치 실행
- [ ] MCP SDK 설치 재시도
- [ ] 설치 성공 확인

### 중기 (내일)
- [ ] pyproject.toml 수정
- [ ] Phase 1 시작
- [ ] 검증 계획 일정 재조정

---

## 📎 참고 자료

### MCP SDK 정보
- [MCP Python SDK - PyPI](https://pypi.org/project/mcp/)
- [GitHub - modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Python SDK Releases](https://github.com/modelcontextprotocol/python-sdk/releases)

### FastMCP 정보
- [FastMCP - PyPI](https://pypi.org/project/fastmcp/)
- [GitHub - jlowin/fastmcp](https://github.com/jlowin/fastmcp)

### Python 설치 가이드
- [Python 3.12 다운로드](https://www.python.org/downloads/)
- [pyenv GitHub](https://github.com/pyenv/pyenv)
- [Homebrew](https://brew.sh/)

---

**보고서 버전**: 1.0
**최종 업데이트**: 2025-11-30
**상태**: 대안 실행 대기 중
**다음 액션**: FastMCP 조사 시작
