# MCP 서버 통합 가이드

**프로젝트**: Other Agents MCP Server
**버전**: 0.1.0
**업데이트**: 2025-12-03

---

## 📋 개요

본 문서는 Other Agents MCP 서버를 다른 서비스 및 애플리케이션에 통합하는 방법을 안내합니다.

### 지원하는 클라이언트

| 클라이언트 | 상태 | 설정 파일 |
|-----------|------|----------|
| **Claude Code** | ✅ 검증 완료 | `.claude/settings.local.json` |
| **Claude Desktop** | ✅ 지원 | `~/.config/claude/mcp_servers.json` |
| **MCP Inspector** | ✅ 테스트 완료 | CLI 실행 |
| **커스텀 클라이언트** | ✅ 지원 | MCP SDK 사용 |

---

## Part 1: Claude Code 통합

### 1.1 설정 파일 위치

```
프로젝트/.claude/settings.local.json
```

### 1.2 설정 방법

#### 옵션 A: 상대 경로 (권장)

**파일**: `.claude/settings.local.json`

```json
{
  "mcpServers": {
    "other-agents-mcp": {
      "command": "./venv/bin/python",
      "args": ["-m", "other_agents_mcp.server"]
    }
  }
}
```

**장점**:
- 어디서든 동일하게 동작
- 경로 문제 없음

**단점**:
- 사용자마다 경로 다름

#### 옵션 B: 상대 경로

```json
{
  "mcpServers": {
    "other-agents-mcp": {
      "command": "python",
      "args": ["-m", "other_agents_mcp.server"],
      "env": {
        "VIRTUAL_ENV": "${workspaceFolder}/venv",
        "PATH": "${workspaceFolder}/venv/bin:${env:PATH}"
      }
    }
  }
}
```

**장점**:
- 프로젝트 이동 시에도 동작

**단점**:
- PATH 설정 필요

### 1.3 동작 확인

#### Claude Code에서 확인

1. Claude Code 재시작
2. MCP 상태 확인:
   ```
   - Tools 탭에 "list_agents", "use_agent" 표시
   ```

#### 테스트 메시지

Claude Code에서:
```
MCP 서버가 연결되었나요? list_agents 도구를 사용해서 확인해주세요.
```

**예상 응답**:
```
네, MCP 서버가 정상적으로 연결되었습니다.
설치된 CLI: claude, gemini, codex, qwen
```

---

## Part 2: Claude Desktop 통합

### 2.1 설정 파일 위치

**macOS/Linux**:
```
~/.config/claude/mcp_servers.json
```

**Windows**:
```
%APPDATA%\Claude\mcp_servers.json
```

### 2.2 설정 방법

#### 전체 설정 파일

**파일**: `~/.config/claude/mcp_servers.json`

```json
{
  "mcpServers": {
    "other-agents-mcp": {
      "command": "/path/to/other-agents/venv/bin/python",
      "args": ["-m", "other_agents_mcp.server"],
      "cwd": "/path/to/other-agents",
      "env": {}
    }
  }
}
```

**주요 필드**:
- `command`: Python 실행 파일 경로 (가상환경)
- `args`: 서버 실행 인자
- `cwd`: 작업 디렉토리 (선택)
- `env`: 환경 변수 (선택)

#### 여러 MCP 서버와 함께 사용

```json
{
  "mcpServers": {
    "other-agents-mcp": {
      "command": "/path/to/other-agents/venv/bin/python",
      "args": ["-m", "other_agents_mcp.server"]
    },
    "other-mcp-server": {
      "command": "node",
      "args": ["/path/to/other-server/index.js"]
    }
  }
}
```

### 2.3 동작 확인

1. **Claude Desktop 재시작**

2. **설정 확인**:
   - Settings → Developer → MCP Servers
   - "other-agents-mcp" 서버 표시 확인

3. **테스트**:
   ```
   사용 가능한 AI CLI 목록을 보여주세요.
   ```

---

## Part 3: MCP Inspector로 테스트

### 3.1 실행 방법

```bash
cd /Users/chans/workspace/pilot/other-agents
source venv/bin/activate
npx @modelcontextprotocol/inspector ./venv/bin/python -m other_agents_mcp.server
```

### 3.2 브라우저 접속

- 자동으로 브라우저 열림
- 수동: `http://localhost:5173`

### 3.3 테스트 체크리스트

- [ ] 서버 연결 확인
- [ ] 2개 도구 표시 (list_agents, use_agent)
- [ ] list_agents 호출 성공
- [ ] use_agent 호출 성공 (설치된 CLI)
- [ ] 프로토콜 검증 통과

---

## Part 4: 커스텀 클라이언트 통합

### 4.1 Python 클라이언트 예제

#### 설치

```bash
pip install mcp
```

#### 클라이언트 코드

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # 서버 파라미터 설정
    server_params = StdioServerParameters(
        command="/Users/chans/workspace/pilot/other-agents/venv/bin/python",
        args=["-m", "other_agents_mcp.server"]
    )

    # 클라이언트 세션 시작
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 초기화
            await session.initialize()

            # 도구 목록 조회
            tools = await session.list_agents()
            print(f"Available tools: {tools}")

            # list_agents 호출
            result = await session.call_tool("list_agents", {})
            print(f"CLIs: {result}")

            # use_agent 호출
            result = await session.call_tool(
                "use_agent",
                {
                    "cli_name": "claude",
                    "message": "Hello!"
                }
            )
            print(f"Response: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 4.2 Node.js 클라이언트 예제

#### 설치

```bash
npm install @modelcontextprotocol/sdk
```

#### 클라이언트 코드

```javascript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

async function main() {
  // 전송 생성
  const transport = new StdioClientTransport({
    command: "/Users/chans/workspace/pilot/other-agents/venv/bin/python",
    args: ["-m", "other_agents_mcp.server"]
  });

  // 클라이언트 생성
  const client = new Client({
    name: "example-client",
    version: "1.0.0"
  }, {
    capabilities: {}
  });

  // 연결
  await client.connect(transport);

  // 도구 목록 조회
  const tools = await client.listTools();
  console.log("Available tools:", tools);

  // list_agents 호출
  const clis = await client.callTool({
    name: "list_agents",
    arguments: {}
  });
  console.log("CLIs:", clis);

  // use_agent 호출
  const response = await client.callTool({
    name: "use_agent",
    arguments: {
      cli_name: "claude",
      message: "Hello!"
    }
  });
  console.log("Response:", response);

  // 연결 종료
  await client.close();
}

main().catch(console.error);
```

---

## Part 5: 환경별 설정

### 5.1 개발 환경

**목적**: 로컬 개발 및 테스트

**설정**:
```json
{
  "mcpServers": {
    "other-agents-mcp": {
      "command": "/path/to/project/venv/bin/python",
      "args": ["-m", "other_agents_mcp.server"],
      "env": {
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

**특징**:
- DEBUG 로그 활성화
- 로컬 경로 사용

### 5.2 프로덕션 환경

**목적**: 안정적인 운영

**설정**:
```json
{
  "mcpServers": {
    "other-agents-mcp": {
      "command": "/usr/local/bin/python3",
      "args": ["-m", "other_agents_mcp.server"],
      "cwd": "/opt/other-agents",
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**특징**:
- INFO 로그 레벨
- 시스템 Python 또는 전역 설치
- 고정된 경로

### 5.3 Docker 환경

#### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 의존성 설치
COPY pyproject.toml .
RUN pip install -e .

# 소스 복사
COPY src/ src/

# MCP 서버 실행
CMD ["python", "-m", "other_agents_mcp.server"]
```

#### Docker Compose

```yaml
version: '3.8'

services:
  other-agents-mcp:
    build: .
    stdin_open: true
    tty: true
```

#### 클라이언트 설정

```json
{
  "mcpServers": {
    "other-agents-mcp": {
      "command": "docker",
      "args": ["run", "-i", "other-agents-mcp"]
    }
  }
}
```

---

## Part 6: 문제 해결

### 6.1 일반적인 문제

#### 문제 1: 서버 연결 실패

**증상**:
```
Error: Failed to connect to MCP server
```

**해결 방법**:

1. **Python 경로 확인**:
   ```bash
   which python
   # 가상환경 경로인지 확인
   ```

2. **서버 직접 실행 테스트**:
   ```bash
   /path/to/venv/bin/python -m other_agents_mcp.server
   ```

3. **Import 에러 확인**:
   ```bash
   python -c "from other_agents_mcp.server import app; print('OK')"
   ```

#### 문제 2: 도구가 표시되지 않음

**원인**: MCP SDK 버전 불일치

**해결**:
```bash
# MCP SDK 버전 확인
pip show mcp

# 업데이트
pip install --upgrade mcp
```

#### 문제 3: 환경 변수 미적용

**증상**: Qwen CLI 등이 동작하지 않음

**해결**:
```json
{
  "mcpServers": {
    "other-agents-mcp": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "other_agents_mcp.server"],
      "env": {
        "OPENAI_API_KEY": "your-api-key",
        "OPENAI_BASE_URL": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
      }
    }
  }
}
```

### 6.2 디버깅 방법

#### 로그 확인

**stderr 출력 보기**:
```bash
# 직접 실행 시 로그 확인
python -m other_agents_mcp.server
```

**로그 레벨 조정**:
```python
# src/other_agents_mcp/logger.py
logger.setLevel(logging.DEBUG)
```

#### MCP Inspector로 디버깅

```bash
npx @modelcontextprotocol/inspector /path/to/venv/bin/python -m other_agents_mcp.server
```

**장점**:
- 실시간 메시지 확인
- 프로토콜 검증
- 도구 테스트

---

## Part 7: 보안 고려사항

### 7.1 권한 관리

**최소 권한 원칙**:
```bash
# 서버 실행 사용자
useradd -r -s /bin/false mcp-server

# 필요한 권한만 부여
chmod 750 /path/to/other-agents
```

### 7.2 임시 파일 보안

**현재 구현**:
- UUID 기반 파일명 (충돌 방지)
- `/tmp` 디렉토리 사용
- 자동 정리 (try-finally)

**추가 강화 (선택)**:
```python
# file_handler.py
import tempfile
import os

# 파일 권한 0600 (소유자만 읽기/쓰기)
fd = os.open(input_path, os.O_CREAT | os.O_WRONLY, 0o600)
```

### 7.3 명령어 인젝션 방지

**현재 구현**:
- `subprocess.run()` 사용 (안전)
- 명령어를 리스트로 전달 (셸 미사용)

**검증 완료**:
```python
# subprocess.run([cmd, arg1, arg2])  ✅ 안전
# subprocess.run(f"{cmd} {arg}")     ❌ 위험
```

---

## Part 8: 성능 최적화

### 8.1 동시 요청 처리

**현재 구현**:
- 비동기 처리 (`asyncio.to_thread`)
- 무상태 서버 (각 요청 독립)

**성능 메트릭**:
- list_agents: <1초
- use_agent (에러): <0.5초
- 동시 5개 요청: <5초

### 8.2 캐싱 (선택)

**CLI 버전 정보 캐싱**:
```python
from functools import lru_cache

@lru_cache(maxsize=10)
def get_cli_version(command: str) -> Optional[str]:
    # 버전 조회 (캐시됨)
    ...
```

**주의**: 캐시 무효화 전략 필요

---

## Part 9: 배포 체크리스트

### 9.1 사전 확인

- [ ] Python 3.10+ 설치 확인
- [ ] MCP SDK 1.22.0+ 설치
- [ ] 가상환경 생성 및 활성화
- [ ] 패키지 설치 (`pip install -e .`)
- [ ] Import 테스트 (`from other_agents_mcp.server import app`)

### 9.2 설정 파일 작성

- [ ] 절대 경로로 Python 지정
- [ ] 환경 변수 설정 (필요 시)
- [ ] 작업 디렉토리 설정 (필요 시)

### 9.3 동작 확인

- [ ] 서버 직접 실행 테스트
- [ ] MCP Inspector 연결 테스트
- [ ] 2개 도구 표시 확인
- [ ] list_agents 호출 성공
- [ ] use_agent 호출 성공 (설치된 CLI)

### 9.4 프로덕션 준비

- [ ] 로그 레벨 설정 (INFO)
- [ ] 에러 모니터링 설정
- [ ] 백업 계획 수립
- [ ] 롤백 계획 수립

---

## Part 10: 비동기 워크플로우 활용 (Leveraging Asynchronous Workflow)

`use_agent`는 간단하지만, 응답이 올 때까지 클라이언트를 차단합니다. 코드 생성이나 데이터 분석처럼 몇 분씩 걸릴 수 있는 긴 작업을 처리하기 위해, 비동기 워크플로우를 사용하는 것이 강력히 권장됩니다.

**핵심 흐름**:
1.  `use_agent`를 호출하여 작업을 시작하고 즉시 `task_id`를 받습니다.
2.  `get_task_status`를 주기적으로 호출(polling)하여 작업 상태를 확인합니다.
3.  상태가 `completed` 또는 `failed`가 되면 폴링을 멈추고 결과를 처리합니다.

### Python 클라이언트 비동기 예제

```python
import asyncio
import time
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command="/Users/chans/workspace/pilot/other-agents/venv/bin/python",
        args=["-m", "other_agents_mcp.server"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 1. 비동기 작업 시작
            print("Starting a long-running task...")
            start_result = await session.call_tool(
                "use_agent",
                {
                    "cli_name": "claude",
                    "message": "Analyze the provided data and generate a 300-line summary report."
                }
            )
            task_id = start_result.get("task_id")
            if not task_id:
                print(f"Failed to start task: {start_result}")
                return

            print(f"Task started with ID: {task_id}")

            # 2. 작업 완료까지 상태 폴링
            while True:
                status_result = await session.call_tool(
                    "get_task_status",
                    {"task_id": task_id}
                )
                
                status = status_result.get("status")
                if status == "completed":
                    print("\nTask completed successfully!")
                    print("Result:", status_result.get("result"))
                    break
                elif status == "failed":
                    print(f"\nTask failed: {status_result.get('error')}")
                    break
                elif status == "running":
                    elapsed = status_result.get('elapsed_time', 0)
                    print(f"Task is still running... ({elapsed:.2f}s elapsed)", end="\r")
                    await asyncio.sleep(5) # 5초마다 확인
                else:
                    print(f"\nUnknown status: {status}")
                    break

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 부록 A: 설정 예제 모음

### Claude Code (개발)

```json
{
  "mcpServers": {
    "other-agents-mcp": {
      "command": "${workspaceFolder}/venv/bin/python",
      "args": ["-m", "other_agents_mcp.server"],
      "env": {
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### Claude Desktop (macOS)

```json
{
  "mcpServers": {
    "other-agents-mcp": {
      "command": "/Users/username/projects/other-agents/venv/bin/python",
      "args": ["-m", "other_agents_mcp.server"],
      "cwd": "/Users/username/projects/other-agents"
    }
  }
}
```

### Claude Desktop (Windows)

```json
{
  "mcpServers": {
    "other-agents-mcp": {
      "command": "C:\\Projects\\other-agents\\venv\\Scripts\\python.exe",
      "args": ["-m", "other_agents_mcp.server"],
      "cwd": "C:\\Projects\\other-agents"
    }
  }
}
```

### Docker

```json
{
  "mcpServers": {
    "other-agents-mcp": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "other-agents-mcp:latest"
      ]
    }
  }
}
```

---

## 부록 B: API 참조

### list_agents

**설명**: 설치된 AI CLI 도구 목록을 조회합니다.

**파라미터**: 없음

**응답**:
```json
{
  "clis": [
    {
      "name": "claude",
      "command": "claude",
      "version": "1.0.0",
      "installed": true
    },
    {
      "name": "gemini",
      "command": "gemini",
      "version": null,
      "installed": false
    }
  ]
}
```

### use_agent

**설명**: 지정한 AI CLI에 메시지를 전송하고 응답을 받습니다.

**파라미터**:
- `cli_name` (string, 필수): CLI 이름 (claude, gemini, codex, qwen)
- `message` (string, 필수): 전송할 프롬프트
- `skip_git_repo_check` (boolean, 선택): Git 저장소 체크 건너뛰기 (Codex만 지원, 기본값: false)

**응답 (성공)**:
```json
{
  "response": "AI의 응답 텍스트"
}
```

**Codex 사용 예시**:
```json
{
  "name": "use_agent",
  "arguments": {
    "cli_name": "codex",
    "message": "Write a fibonacci function",
    "skip_git_repo_check": true
  }
}
```

**응답 (에러)**:
```json
{
  "error": "CLI not found: nonexistent-cli",
  "type": "CLINotFoundError"
}
```

**에러 타입**:
- `CLINotFoundError`: CLI가 설치되지 않음
- `CLITimeoutError`: 실행 타임아웃 (60초)
- `CLIExecutionError`: CLI 실행 중 에러

---

**문서 버전**: 1.0
**최종 업데이트**: 2025-11-30
**작성자**: Claude Code

**관련 문서**:
- `README.md` - 프로젝트 개요
- `docs/ARCHITECTURE.md` - 시스템 아키텍처
- `tests/mcp-validation/TESTING_GUIDE.md` - 테스트 가이드
- `tests/mcp-validation/VALIDATION_REPORT.md` - 검증 보고서
