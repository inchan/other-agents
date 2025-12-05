# Phase 1: MCP Inspector 수동 테스트 가이드

**작성 일자**: 2025-11-30
**대상**: AI CLI Ping-Pong MCP Server
**도구**: MCP Inspector

---

## 🎯 테스트 목표

1. MCP 서버가 정상적으로 시작되는지 확인
2. MCP Inspector와 연결되는지 확인
3. 2개 도구(list_available_clis, send_message)가 표시되는지 확인
4. 프로토콜 및 스키마 검증 통과 확인

---

## 📋 사전 준비

### 1. 가상 환경 활성화

```bash
cd /Users/chans/workspace/pilot/other-agents
source venv/bin/activate
```

**확인**:
```bash
which python
# 출력: /Users/chans/workspace/pilot/other-agents/venv/bin/python

python --version
# 출력: Python 3.12.12
```

---

### 2. MCP 서버 작동 확인

```bash
python -c "from other_agents_mcp.server import app; print('Server:', app.name)"
```

**예상 출력**:
```
Server: other-agents-mcp
```

---

## 🚀 MCP Inspector 실행

### 방법 1: 직접 실행 (권장)

**터미널에서 실행**:
```bash
npx @modelcontextprotocol/inspector ./venv/bin/python -m other_agents_mcp.server
```

**예상 출력**:
```
Starting MCP Inspector...
Server running at http://localhost:5173
Opening browser...
```

**다음 단계**:
- 자동으로 브라우저가 열립니다
- URL: `http://localhost:5173`
- 수동으로 열기: 위 URL을 브라우저에 입력

---

### 방법 2: 백그라운드 실행

**터미널 1 (Inspector 실행)**:
```bash
npx @modelcontextprotocol/inspector ./venv/bin/python -m other_agents_mcp.server
```

**브라우저**:
- `http://localhost:5173` 접속

---

## ✅ 테스트 체크리스트

### 1단계: 서버 연결 확인

- [ ] MCP Inspector UI가 브라우저에서 열림
- [ ] "Connected to server" 메시지 확인
- [ ] 서버 이름 "other-agents-mcp" 표시
- [ ] 연결 상태가 녹색/활성으로 표시

**스크린샷 위치**: (선택) `tests/mcp-validation/screenshots/01-connection.png`

---

### 2단계: 도구 목록 확인

**확인 사항**:
- [ ] 도구가 2개 표시됨
- [ ] 첫 번째 도구: `list_available_clis`
- [ ] 두 번째 도구: `send_message`

**도구 1: list_available_clis**
- [ ] 이름: "list_available_clis"
- [ ] 설명: "설치된 AI CLI 목록 조회"
- [ ] inputSchema: `{"type": "object", "properties": {}}`
- [ ] Required parameters: 없음

**도구 2: send_message**
- [ ] 이름: "send_message"
- [ ] 설명: "AI CLI에 메시지 전송 (파일 기반)"
- [ ] inputSchema에 2개 속성:
  - [ ] `cli_name` (string)
  - [ ] `message` (string)
- [ ] Required parameters: `["cli_name", "message"]`

---

### 3단계: 프로토콜 검증

**MCP Inspector 검증 패널 확인**:
- [ ] "Protocol Validation: PASSED" 표시
- [ ] 스키마 검증 통과
- [ ] 경고 메시지 없음
- [ ] 에러 메시지 없음

**검증 항목**:
- [ ] JSON-RPC 2.0 형식 준수
- [ ] MCP 메시지 구조 정확성
- [ ] 도구 스키마 유효성 (JSON Schema 준수)

---

### 4단계: list_available_clis 도구 테스트

**실행 방법**:
1. Inspector UI에서 "list_available_clis" 도구 선택
2. 파라미터 입력: (없음)
3. "Call Tool" 버튼 클릭

**예상 결과**:
```json
{
  "clis": [
    {
      "name": "claude",
      "version": "x.x.x",
      "path": "/path/to/claude"
    },
    // ... 기타 설치된 CLI
  ]
}
```

**확인 사항**:
- [ ] 응답이 JSON 형식
- [ ] `clis` 배열 포함
- [ ] 각 CLI에 `name`, `version`, `path` 포함
- [ ] 에러 없이 완료
- [ ] 응답 시간 2초 이내

**실제 결과 기록**:
```
# 여기에 실제 응답 기록
```

---

### 5단계: send_message 도구 테스트 (정상 케이스)

**테스트 케이스 1: Claude CLI**

**입력**:
```json
{
  "cli_name": "claude",
  "message": "Hello, this is a test message"
}
```

**실행**:
1. Inspector UI에서 "send_message" 도구 선택
2. 위 JSON 입력
3. "Call Tool" 버튼 클릭

**예상 결과**:
```json
{
  "response": "Claude CLI의 응답 텍스트..."
}
```

**확인 사항**:
- [ ] 응답에 `response` 필드 포함
- [ ] 응답이 문자열 형식
- [ ] 에러 없이 완료
- [ ] CLI가 실제로 실행됨

**실제 결과 기록**:
```
# 여기에 실제 응답 기록
```

---

### 6단계: 에러 핸들링 테스트

**테스트 케이스 2: 존재하지 않는 CLI**

**입력**:
```json
{
  "cli_name": "nonexistent-cli",
  "message": "test"
}
```

**예상 결과**:
```json
{
  "error": "CLI not found: nonexistent-cli",
  "type": "CLINotFoundError"
}
```

**확인 사항**:
- [ ] 에러 응답 수신
- [ ] `error` 필드에 명확한 메시지
- [ ] `type` 필드에 "CLINotFoundError"
- [ ] 서버가 크래시하지 않음

---

**테스트 케이스 3: 필수 파라미터 누락**

**입력**:
```json
{
  "cli_name": "claude"
  // message 누락
}
```

**예상 결과**:
```json
{
  "error": "Missing required parameter: message"
  // 또는 MCP 프로토콜 레벨 에러
}
```

**확인 사항**:
- [ ] 에러 메시지 수신
- [ ] 파라미터 검증 작동
- [ ] 서버가 안정적으로 유지

---

### 7단계: 실시간 로그 확인

**터미널 로그 확인**:

MCP Inspector를 실행한 터미널에서 다음 로그 확인:

```
AI CLI Ping-Pong MCP Server starting...
MCP SDK version: 1.22.0
Server name: other-agents-mcp
Available tools: list_available_clis, send_message
```

**도구 호출 시 로그**:
- [ ] 도구 호출 로그 출력
- [ ] 에러 발생 시 에러 로그
- [ ] 타임스탬프 포함

---

### 8단계: 성능 측정

**응답 시간 측정**:

각 도구 호출의 응답 시간을 Inspector UI에서 확인:

| 도구 | 테스트 케이스 | 응답 시간 | 목표 | 통과 여부 |
|------|--------------|----------|------|-----------|
| list_available_clis | 정상 | ___ ms | <2000ms | ☐ |
| send_message | claude | ___ ms | <5000ms | ☐ |
| send_message | 에러 | ___ ms | <1000ms | ☐ |

---

## 🐛 문제 해결 (Troubleshooting)

### 문제 1: Inspector가 시작되지 않음

**증상**:
```
Error: Cannot find module '@modelcontextprotocol/inspector'
```

**해결**:
```bash
# npm 캐시 정리 후 재시도
npm cache clean --force
npx @modelcontextprotocol/inspector ./venv/bin/python -m other_agents_mcp.server
```

---

### 문제 2: 서버 연결 실패

**증상**:
Inspector UI에 "Failed to connect to server" 표시

**확인 사항**:
1. Python 가상 환경 활성화 여부
2. 서버 경로가 정확한지 확인
   ```bash
   ./venv/bin/python -m other_agents_mcp.server
   ```
3. MCP SDK 설치 확인
   ```bash
   ./venv/bin/pip show mcp
   ```

**해결**:
- Inspector 재시작
- 서버 경로 절대 경로로 변경
  ```bash
  npx @modelcontextprotocol/inspector /Users/chans/workspace/pilot/other-agents/venv/bin/python -m other_agents_mcp.server
  ```

---

### 문제 3: 도구가 표시되지 않음

**증상**:
Inspector에서 도구 목록이 비어 있음

**확인**:
1. `server.py`의 `@app.list_tools()` 데코레이터 확인
2. import 에러 확인
   ```bash
   ./venv/bin/python -c "from other_agents_mcp.server import app, list_tools"
   ```

---

### 문제 4: 도구 호출 시 에러

**증상**:
```json
{
  "error": "Internal server error"
}
```

**디버깅**:
1. 터미널 로그 확인 (자세한 에러 메시지)
2. Python 직접 테스트
   ```bash
   ./venv/bin/python -c "
   from other_agents_mcp.cli_manager import list_available_clis
   print(list_available_clis())
   "
   ```

---

## 📊 테스트 결과 요약

### 성공 기준

- [x] ~~서버 연결 성공~~
- [ ] 2개 도구 표시
- [ ] 프로토콜 검증 통과
- [ ] list_available_clis 정상 동작
- [ ] send_message 정상 동작
- [ ] 에러 핸들링 정상 동작
- [ ] 응답 시간 목표 달성

### 발견된 이슈

**Issue #1**: (예시)
- **증상**:
- **재현 방법**:
- **심각도**: Critical / Major / Minor
- **해결 방법**:

---

## 📝 다음 단계

### Phase 1 완료 후

**성공 시**:
- Phase 2 (기술 테스트) 착수
- 자동화된 pytest 테스트 작성

**실패 시**:
- 발견된 이슈 수정
- Phase 1 재테스트

---

## 🔗 참고 자료

- [MCP Inspector 공식 문서](https://modelcontextprotocol.io/docs/tools/inspector)
- [MCP Protocol Specification](https://modelcontextprotocol.io/specification/)
- [Phase 0 Success Report](./PHASE0_SUCCESS_REPORT.md)

---

**가이드 버전**: 1.0
**최종 업데이트**: 2025-11-30
**상태**: Phase 1 테스트 준비 완료
