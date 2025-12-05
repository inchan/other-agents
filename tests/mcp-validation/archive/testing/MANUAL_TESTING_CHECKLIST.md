# MCP Inspector 수동 테스트 체크리스트

**작성 일자**: 2025-11-30
**Phase**: Phase 3 - 행동 테스트
**목적**: MCP 서버의 실제 동작을 MCP Inspector를 통해 검증

---

## 📋 테스트 환경 설정

### 사전 준비

- [ ] 가상 환경 활성화 완료 (`source venv/bin/activate`)
- [ ] Python 3.12.12 확인 (`python --version`)
- [ ] MCP SDK 1.22.0 설치 확인
- [ ] 패키지 editable install 확인 (`pip show other-agents-mcp`)

### Inspector 설치 확인

```bash
npx @modelcontextprotocol/inspector --version
```

---

## 🚀 서버 시작 및 연결

### 1. 서버 시작

**실행 명령어**:
```bash
npx @modelcontextprotocol/inspector ./venv/bin/python -m other_agents_mcp.server
```

**체크리스트**:
- [ ] Inspector가 정상적으로 시작됨
- [ ] 브라우저 자동 실행 또는 URL 표시
- [ ] 기본 URL: `http://localhost:5173` (또는 표시된 포트)
- [ ] 서버 프로세스가 백그라운드에서 실행 중

### 2. 연결 상태 확인

**Inspector UI에서 확인**:
- [ ] "Connected" 상태 표시
- [ ] 서버 이름 표시: `other-agents-mcp`
- [ ] 연결 시간 표시
- [ ] 에러 메시지 없음
- [ ] 로그 출력 확인 가능

---

## 🔧 도구 목록 검증

### 3. 도구 개수 확인

**체크리스트**:
- [ ] 정확히 2개 도구 표시
- [ ] 도구 이름 표시 정확
- [ ] 도구 설명 표시 정확

### 4. list_available_clis 도구 확인

**도구 정보**:
- [ ] 이름: `list_available_clis`
- [ ] 설명: "설치된 AI CLI 목록 조회"
- [ ] inputSchema 존재
- [ ] inputSchema.type = "object"
- [ ] inputSchema.properties = {} (빈 객체)
- [ ] required 필드 없음

### 5. send_message 도구 확인

**도구 정보**:
- [ ] 이름: `send_message`
- [ ] 설명: "AI CLI에 메시지 전송 (파일 기반)"
- [ ] inputSchema 존재
- [ ] inputSchema.type = "object"
- [ ] inputSchema.properties 포함: `cli_name`, `message`
- [ ] required 필드: `["cli_name", "message"]`

**cli_name 속성**:
- [ ] type: "string"
- [ ] description 존재
- [ ] 예시 값 표시: "claude, gemini, codex, qwen"

**message 속성**:
- [ ] type: "string"
- [ ] description 존재
- [ ] "전송할 프롬프트" 설명

---

## ✅ 기능 테스트 - list_available_clis

### 6. 정상 호출 테스트

**실행**:
1. Inspector UI에서 `list_available_clis` 선택
2. 파라미터 없이 실행 (빈 객체 `{}`)

**체크리스트**:
- [ ] 도구 호출 성공
- [ ] 응답 받음 (2초 이내)
- [ ] 응답 형식: `{"clis": [...]}`
- [ ] clis가 배열임
- [ ] 각 CLI 항목 구조 확인:
  - [ ] `name` (string)
  - [ ] `command` (string)
  - [ ] `version` (string or null)
  - [ ] `installed` (boolean)

**예상 CLI 목록**:
- [ ] claude
- [ ] gemini
- [ ] codex
- [ ] qwen

### 7. 응답 데이터 검증

**각 CLI 항목 확인**:
- [ ] `installed: true`인 CLI의 `version`이 null이 아님
- [ ] `installed: false`인 CLI의 `version`이 null
- [ ] `command` 값이 실제 명령어와 일치 (claude, gemini, codex, qwen)

---

## ✅ 기능 테스트 - send_message

### 8. 정상 호출 테스트 (Claude CLI)

**조건**: Claude CLI가 설치되어 있어야 함

**실행**:
1. `send_message` 도구 선택
2. 파라미터 입력:
   ```json
   {
     "cli_name": "claude",
     "message": "Hello! This is a test message."
   }
   ```

**체크리스트**:
- [ ] 도구 호출 시작
- [ ] 응답 받음 (60초 이내)
- [ ] 응답 형식: `{"response": "..."}`
- [ ] response 값이 문자열
- [ ] response 길이 > 0
- [ ] 에러 없음

### 9. 에러 테스트 - CLI Not Found

**실행**:
1. `send_message` 도구 선택
2. 파라미터 입력:
   ```json
   {
     "cli_name": "nonexistent-cli",
     "message": "test"
   }
   ```

**체크리스트**:
- [ ] 도구 호출 성공 (호출 자체는 성공)
- [ ] 응답 받음 (즉시)
- [ ] 응답 형식: `{"error": "...", "type": "..."}`
- [ ] error 메시지 포함
- [ ] type = "CLINotFoundError"
- [ ] 에러 메시지가 명확함

### 10. 에러 테스트 - Missing Parameter

**실행**:
1. `send_message` 도구 선택
2. 파라미터 입력 (message 누락):
   ```json
   {
     "cli_name": "claude"
   }
   ```

**체크리스트**:
- [ ] 파라미터 검증 에러 발생
- [ ] 에러 메시지 표시
- [ ] "message" 누락 관련 메시지
- [ ] 도구 실행 차단됨 (또는 에러 응답)

### 11. 에러 테스트 - Empty Message

**실행**:
1. `send_message` 도구 선택
2. 파라미터 입력:
   ```json
   {
     "cli_name": "claude",
     "message": ""
   }
   ```

**체크리스트**:
- [ ] 도구 호출 성공 또는 검증 에러
- [ ] 빈 메시지 처리 확인
- [ ] 에러 또는 빈 응답

---

## 📊 프로토콜 준수 검증

### 12. MCP 프로토콜 검증

**Inspector 자동 검증**:
- [ ] JSON-RPC 2.0 형식 준수
- [ ] 스키마 검증 통과
- [ ] 메시지 형식 정확
- [ ] 에러 형식 정확

**로그 확인**:
- [ ] 요청 로그 출력
- [ ] 응답 로그 출력
- [ ] 타임스탬프 포함
- [ ] 로그 레벨 적절 (INFO, DEBUG, ERROR)

### 13. 스키마 준수 확인

**JSON Schema 검증**:
- [ ] inputSchema가 유효한 JSON Schema
- [ ] type, properties, required 올바름
- [ ] description 모든 필드 포함
- [ ] 경고나 에러 없음

---

## 🔄 동작 검증

### 14. 연속 호출 테스트

**실행**:
1. `list_available_clis` 3회 연속 호출
2. 각 호출 간격 1초

**체크리스트**:
- [ ] 모든 호출 성공
- [ ] 응답 일관성 (동일한 결과)
- [ ] 메모리 누수 없음
- [ ] 서버 안정성 유지

### 15. 교차 호출 테스트

**실행**:
1. `list_available_clis` 호출
2. `send_message` 호출 (존재하지 않는 CLI)
3. `list_available_clis` 호출
4. `send_message` 호출 (정상 CLI)

**체크리스트**:
- [ ] 모든 호출 순서대로 성공
- [ ] 에러 발생 후 정상 복구
- [ ] 상태 유지 (무상태 서버 확인)
- [ ] 각 호출이 독립적

---

## 📈 성능 검증

### 16. 응답 시간 측정

**list_available_clis**:
- [ ] 평균 응답 시간: < 1초
- [ ] 최대 응답 시간: < 2초

**send_message** (정상 CLI):
- [ ] 평균 응답 시간: < 30초
- [ ] 최대 응답 시간: < 60초 (타임아웃)

**send_message** (에러):
- [ ] 평균 응답 시간: < 0.5초
- [ ] 즉각적인 에러 반환

### 17. 리소스 사용량

**메모리**:
- [ ] 서버 시작 시 메모리 사용량 기록
- [ ] 10회 호출 후 메모리 사용량 확인
- [ ] 메모리 누수 없음 (증가율 < 10%)

**CPU**:
- [ ] 유휴 시 CPU 사용량 < 5%
- [ ] 호출 중 CPU 사용량 < 50%

---

## 🐛 에러 처리 검증

### 18. 예외 상황 테스트

**서버 재시작**:
- [ ] 서버 중단 후 재시작
- [ ] Inspector 재연결 성공
- [ ] 모든 기능 정상 작동

**네트워크 지연 시뮬레이션**:
- [ ] 느린 CLI 응답 처리
- [ ] 타임아웃 정상 작동
- [ ] 에러 메시지 명확

---

## 📝 로그 검증

### 19. 로그 출력 확인

**서버 로그**:
- [ ] 시작 메시지 출력
- [ ] 도구 호출 로그
- [ ] 에러 로그 (에러 발생 시)
- [ ] 타임스탬프 포함
- [ ] 로그 레벨 명시 (INFO, DEBUG, ERROR)

**Inspector 로그**:
- [ ] 요청 메시지 표시
- [ ] 응답 메시지 표시
- [ ] JSON 형식 정확
- [ ] 읽기 쉬운 포맷

---

## ✅ 최종 검증

### 20. 전체 워크플로우 테스트

**시나리오**:
1. 서버 시작
2. CLI 목록 조회
3. 설치된 CLI 확인
4. 메시지 전송 (정상)
5. 에러 케이스 테스트
6. 다시 정상 호출
7. 서버 종료

**체크리스트**:
- [ ] 전체 흐름 정상 작동
- [ ] 모든 단계 성공
- [ ] 에러 복구 확인
- [ ] 최종 상태 정상

---

## 📊 테스트 결과 기록

### Hit Rate 측정

**정의**: 요청한 도구가 올바르게 실행된 비율

- 총 호출 수: ______
- 성공 수: ______
- 실패 수: ______
- **Hit Rate**: ______% (목표: 95%+)

### Success Rate 측정

**정의**: 도구 실행이 예상된 결과를 반환한 비율

- 총 실행 수: ______
- 성공 수: ______
- 에러 수: ______
- **Success Rate**: ______% (목표: 99%+)

### 응답 시간 통계

**list_available_clis**:
- 평균: ______ ms
- 최소: ______ ms
- 최대: ______ ms
- 중앙값: ______ ms

**send_message**:
- 평균: ______ ms
- 최소: ______ ms
- 최대: ______ ms
- 중앙값: ______ ms

---

## 🎯 성공 기준

### 필수 기준 (모두 충족 필요)

- [ ] ✅ 서버 시작 및 연결 성공
- [ ] ✅ 2개 도구 모두 표시
- [ ] ✅ 모든 필수 속성 존재
- [ ] ✅ 프로토콜 검증 통과
- [ ] ✅ 정상 케이스 모두 성공
- [ ] ✅ 에러 케이스 적절히 처리
- [ ] ✅ Hit Rate ≥ 95%
- [ ] ✅ Success Rate ≥ 99%

### 권장 기준

- [ ] 응답 시간 목표 달성
- [ ] 메모리 누수 없음
- [ ] 로그 품질 우수
- [ ] 에러 메시지 명확

---

## 📌 참고 사항

### 알려진 제한사항

1. CLI가 설치되지 않은 경우 `send_message` 테스트 제한
2. 네트워크 환경에 따른 응답 시간 변동
3. CLI 버전에 따른 동작 차이

### 문제 발생 시 조치

1. **서버 연결 실패**:
   - 가상 환경 확인
   - 포트 충돌 확인
   - 서버 재시작

2. **도구 호출 실패**:
   - 로그 확인
   - 파라미터 형식 확인
   - CLI 설치 여부 확인

3. **타임아웃**:
   - CLI 동작 확인
   - 네트워크 확인
   - 타임아웃 설정 확인

---

**테스트 수행자**: _______________
**테스트 일자**: _______________
**테스트 환경**: macOS (Darwin 25.1.0), Python 3.12.12
**테스트 결과**: ⬜ 통과 / ⬜ 실패 / ⬜ 부분 통과

**비고**:
```
(테스트 중 발견한 이슈나 특이사항 기록)
```

---

**문서 버전**: 1.0
**최종 업데이트**: 2025-11-30
