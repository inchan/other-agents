# Usage Examples - 사용 예시

## 자연어로 AI CLI 호출하기

Claude Code는 MCP 도구 설명을 읽고 자동으로 적절한 도구를 선택합니다.

### 단일 AI에게 요청

#### Codex에게 리뷰 요청
```
사용자: "codex에게 이 코드 리뷰 요청해줘"

→ Claude가 자동으로 선택:
  use_agent(
    cli_name="codex",
    message="다음 코드를 리뷰해주세요: [현재 파일 내용]"
  )
```

#### Gemini에게 질문
```
사용자: "gemini한테 물어봐: 이 함수를 어떻게 최적화할 수 있을까?"

→ Claude가 자동으로 선택:
  use_agent(
    cli_name="gemini",
    message="이 함수를 어떻게 최적화할 수 있을까? [함수 코드]"
  )
```

#### Qwen에게 번역 요청
```
사용자: "qwen한테 이 주석을 한국어로 번역해달라고 해줘"

→ Claude가 자동으로 선택:
  use_agent(
    cli_name="qwen",
    message="다음 주석을 한국어로 번역해주세요: [주석 내용]"
  )
```

### 여러 AI에게 동시 요청

#### 특정 AI들에게
```
사용자: "claude, gemini, codex에게 이 아키텍처에 대한 의견 물어봐"

→ Claude가 자동으로 선택:
  use_agents(
    cli_names=["claude", "gemini", "codex"],
    message="이 아키텍처에 대한 의견을 알려주세요: [아키텍처 설명]"
  )
```

#### 모든 AI에게
```
사용자: "모든 AI에게 리뷰 요청해줘"

→ Claude가 자동으로 선택:
  use_agents(
    message="다음 코드를 리뷰해주세요: [코드]"
    # cli_names 생략 시 모든 사용 가능한 CLI에게 전송
  )
```

#### 비교 분석
```
사용자: "여러 AI의 의견을 들어보고 싶어. 이 함수의 성능 개선 방법을 물어봐줘"

→ Claude가 자동으로 선택:
  use_agents(
    message="이 함수의 성능 개선 방법을 제안해주세요: [함수 코드]"
  )

→ Claude가 각 AI의 응답을 정리해서 사용자에게 제공
```

## 주요 키워드

Claude는 다음 키워드들을 인식하여 적절한 도구를 선택합니다:

### AI 이름 인식
- "codex", "Codex", "코덱스" → cli_name="codex"
- "claude", "Claude", "클로드" → cli_name="claude"
- "gemini", "Gemini", "제미나이" → cli_name="gemini"
- "qwen", "Qwen", "큐웬" → cli_name="qwen"

### 행동 패턴 인식
- "~에게", "~한테" → use_agent 선택
- "모두에게", "여러 AI", "다양한 의견" → use_agents 선택
- "리뷰", "검토", "평가" → 코드 리뷰 요청
- "물어봐", "질문", "의견" → 질문 전달

## 팁

### 1. 명확한 AI 이름 사용
✅ 좋은 예: "codex에게 리뷰 요청"
❌ 나쁜 예: "커서한테 물어봐" (Claude가 어떤 CLI인지 모를 수 있음)

### 2. 구체적인 요청
✅ 좋은 예: "gemini에게 이 함수의 시간복잡도 분석 요청"
❌ 나쁜 예: "분석해줘" (어느 AI인지, 무엇을 분석할지 불명확)

### 3. 여러 의견이 필요할 때
✅ 좋은 예: "모든 AI에게 이 디자인 패턴의 장단점 물어봐"
→ 다양한 관점에서 답변을 받을 수 있음

### 4. 컨텍스트 제공
Claude는 현재 파일이나 선택된 코드를 자동으로 포함하지만,
추가 컨텍스트가 필요한 경우 명시적으로 언급:
```
"codex에게 AuthService.ts와 연관지어서 이 함수 리뷰 요청"
```

## 고급 사용법

### 세션 모드
```
사용자: "gemini와 세션 시작해서 계속 대화하고 싶어"

→ Claude가 자동으로:
  1. 첫 요청 시 session_id 생성
  2. 이후 대화에서 같은 session_id 재사용
  3. resume=true로 컨텍스트 유지
```

### 비동기 실행 (긴 작업)
```
사용자: "codex에게 전체 코드베이스 분석 요청 (시간 걸릴 것 같아)"

→ Claude가 자동으로:
  use_agent(
    cli_name="codex",
    message="...",
    run_async=true  # 백그라운드 실행
  )

  # 주기적으로 상태 확인
  get_task_status(task_id="...")
```

## 문제 해결

### "CLI를 찾을 수 없습니다" 에러
```
사용자: "codex 설치되어 있나 확인해줘"

→ Claude가 자동으로:
  list_agents()

→ 설치된 CLI 목록과 상태 확인
```

### AI가 응답하지 않을 때
- 타임아웃 기본값: 300초 (5분)
- 필요시 타임아웃 조정 가능
- 비동기 모드 사용 권장 (긴 작업)

## 참고

모든 도구 설명과 파라미터는 MCP 프로토콜을 통해 Claude에게 자동으로 전달됩니다.
사용자는 자연어로 요청만 하면 Claude가 적절한 도구를 선택하여 실행합니다.
