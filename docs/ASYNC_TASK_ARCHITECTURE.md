# 비동기 작업 실행 아키텍처 (Asynchronous Task Execution Architecture)

## 1. 문제 정의

기존의 `use_agent` 도구는 동기적으로(synchronously) 동작하여, AI CLI의 작업이 끝날 때까지 클라이언트의 요청을 차단(blocking)하는 문제가 있습니다. 이로 인해 수 분이 소요되는 긴 작업의 경우, 클라이언트는 응답이 올 때까지 아무것도 하지 못하고 기다려야 합니다.

이 문제를 해결하기 위해 '인터랙티브 타임아웃'(`elicit` 활용) 방식을 초기에 고려했으나, 클라이언트가 항상 인간 사용자라는 잘못된 전제에 기반하고 있어 AI 에이전트 등 자동화된 클라이언트와의 호환성 문제가 발생하는 치명적 설계 결함이 발견되었습니다.

따라서 모든 종류의 클라이언트를 안정적으로 지원할 수 있는 새로운 아키텍처가 필요합니다.

## 2. 해결 아키텍처: 비동기 작업 + 상태 폴링

업계 표준(de-facto standard)인 '비동기 작업 + 상태 폴링(Polling)' 모델을 채택합니다. 이 모델은 작업의 '요청'과 '결과 확인'을 명확히 분리하여 클라이언트의 블로킹을 없애고, 시스템의 견고성과 유연성을 극대화합니다.

**작동 흐름:**
1.  클라이언트는 `use_agent`를 호출하여 긴 작업을 요청합니다.
2.  서버는 즉시 작업을 백그라운드에서 시작하고, 해당 작업을 추적할 수 있는 고유한 `task_id`를 클라이언트에게 즉시 반환합니다.
3.  클라이언트는 받은 `task_id`를 사용하여, 원하는 시점에 `get_task_status`를 주기적으로 호출하여 작업의 진행 상태를 확인(Polling)합니다.
4.  작업이 완료되면, `get_task_status`의 응답에 최종 결과 또는 에러가 포함됩니다. 클라이언트는 이 응답을 받고 폴링을 중단합니다.

## 3. 새로운 API 명세 (Tools)

### 3.1 `use_agent`

긴 작업을 시작하고 즉시 `task_id`를 반환합니다.

-   **Input Schema:**
    -   기존 `use_agent`의 모든 파라미터 (`cli_name`, `message`, `system_prompt`, `args`, `timeout` 등)를 동일하게 사용합니다.
-   **Output Schema (즉시 반환):**
    ```json
    {
      "task_id": "<unique-task-identifier>"
    }
    ```

### 3.2 `get_task_status`

`task_id`를 사용하여 작업의 현재 상태와 결과(완료 시)를 조회합니다.

-   **Input Schema:**
    ```json
    {
      "task_id": {
        "type": "string",
        "description": "use_agent로부터 받은 작업 ID"
      }
    }
    ```
-   **Output Schema:**
    -   **작업 진행 중:**
        ```json
        {
          "status": "running",
          "elapsed_time": 120 // (초 단위 경과 시간)
        }
        ```
    -   **작업 완료:**
        ```json
        {
          "status": "completed",
          "result": "<CLI 실행 결과 문자열>"
        }
        ```
    -   **작업 실패:**
        ```json
        {
          "status": "failed",
          "error": "<에러 메시지>"
        }
        ```
    -   **작업을 찾을 수 없음:**
        ```json
        {
          "status": "not_found",
          "error": "Task ID not found or expired."
        }
        ```

## 4. 단계별 구현 전략

### 1단계: MVP (최소 기능 제품)

빠른 가치 검증을 위해 핵심 기능에 집중합니다.

1.  **Task Manager 구현:**
    -   서버 내부에 작업 상태를 관리할 `TaskManager` 클래스를 구현합니다.
    -   저장소(Storage)를 교체할 수 있도록, 저장소 로직을 분리한 **인터페이스 기반으로 설계**합니다. (`Strategy Pattern`)
2.  **In-Memory Storage 구현:**
    -   작업 상태를 Python `dict`를 사용하여 메모리에 저장하는 `InMemoryStorage` 클래스를 구현하여 `TaskManager`에 주입합니다.
3.  **리소스 관리:**
    -   메모리 누수를 방지하기 위해, 완료/실패된 작업은 **1시간 후 자동으로 삭제**되는 TTL(Time-To-Live) 기반의 간단한 쓰레기 수집(Garbage Collection) 로직을 필수로 구현합니다.
4.  **한계점 명시:**
    -   이 단계의 명백한 한계점은 **"서버 재시작 시 모든 작업 내역이 유실된다"**는 것입니다. 이 내용은 문서와 로그에 명확히 기록합니다.

### 2단계: 견고성 강화

MVP의 기능이 검증된 후, 시스템의 안정성을 높입니다.

1.  **SQLite Storage 구현:**
    -   1단계에서 정의한 저장소 인터페이스를 따르는 `SqliteStorage` 클래스를 구현합니다. Python에 내장된 `sqlite3` 모듈을 사용하여 외부 의존성 없이 영속성을 확보합니다.
2.  **저장소 교체:**
    -   서버 시작 시 `TaskManager`에 `InMemoryStorage` 대신 `SqliteStorage`를 주입합니다. 설계가 잘 되어있다면 이 교체 작업은 매우 간단합니다.
3.  **재시작 복구 로직:**
    -   서버가 재시작될 때, `SqliteStorage`는 DB에 'running' 상태로 남아있던 모든 작업을 'failed' (사유: "Server restarted") 상태로 변경하는 복구 로지을 구현하여 클라이언트가 작업의 비정상 종료를 인지할 수 있게 합니다.

---
이 문서는 새로운 비동기 작업 처리 기능의 설계와 구현 계획을 정의합니다.
