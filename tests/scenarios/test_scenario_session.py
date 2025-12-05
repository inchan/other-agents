"""장기 세션 및 컨텍스트 시나리오 테스트

pytest 통합 버전
주의: 이 테스트는 장시간(350초+) 소요됩니다.
일반 테스트 실행 시 제외하려면: pytest -m "not slow"
"""
import asyncio
import pytest

from other_agents_mcp.server import call_tool
from other_agents_mcp.task_manager import get_task_manager, InMemoryStorage


@pytest.fixture(autouse=True)
def reset_task_manager():
    """각 테스트 전에 TaskManager를 초기화"""
    task_manager = get_task_manager()
    task_manager.storage = InMemoryStorage()
    yield


@pytest.fixture
async def session_bot():
    """세션 지원 테스트용 CLI 'session-bot' 추가 (350초 지연)"""
    await call_tool("add_tool", {
        "name": "session-bot",
        "command": "bash",
        "extra_args": ["-c", "sleep 350 && cat"],
        "supported_args": ["-c", "--session-id", "--resume"],
        "timeout": 360
    })
    return "session-bot"


@pytest.fixture
async def fast_session_bot():
    """빠른 세션 테스트용 CLI (지연 없음)"""
    await call_tool("add_tool", {
        "name": "fast-session-bot",
        "command": "cat",
        "supported_args": ["--session-id", "--resume"],
        "timeout": 60
    })
    return "fast-session-bot"


@pytest.mark.slow
class TestLongRunningSessionScenarios:
    """장시간 실행 세션 시나리오 (350초+ 소요)

    실행: pytest -m slow
    제외: pytest -m "not slow"
    """

    async def test_session_start(self, session_bot):
        """[Session] 세션 시작"""
        result = await call_tool("run_tool", {
            "cli_name": session_bot,
            "message": "My info",
            "session_id": "my-long-session-001"
        })

        assert "response" in result

    async def test_session_resume(self, session_bot):
        """[Session] 세션 재개 (Resume)"""
        # 먼저 세션 시작
        await call_tool("run_tool", {
            "cli_name": session_bot,
            "message": "Initial message",
            "session_id": "my-long-session-001"
        })

        # 세션 재개
        result = await call_tool("run_tool", {
            "cli_name": session_bot,
            "message": "Recall info",
            "session_id": "my-long-session-001",
            "resume": True
        })

        assert "response" in result

    async def test_async_session_with_long_wait(self, session_bot):
        """[Session + Async] 비동기 세션 요청 (350초 이상 대기)"""
        result = await call_tool("run_tool", {
            "cli_name": session_bot,
            "message": "Async Session Work",
            "session_id": "my-long-session-001",
            "run_async": True
        })

        assert "task_id" in result
        task_id = result["task_id"]

        # 360초 동안 1초 간격 폴링
        for i in range(360):
            status = await call_tool("get_run_status", {"task_id": task_id})
            if status["status"] == "completed":
                assert "Async Session Work" in status["result"]
                return
            await asyncio.sleep(1)

        pytest.fail("Timeout waiting for long-running async task")

    async def test_different_session_id(self, session_bot):
        """[Session] 다른 세션 ID 사용"""
        result = await call_tool("run_tool", {
            "cli_name": session_bot,
            "message": "Other session",
            "session_id": "other-session-002"
        })

        assert "response" in result


class TestFastSessionScenarios:
    """빠른 세션 시나리오 (일반 테스트에 포함)"""

    async def test_session_basic_flow(self, fast_session_bot):
        """[Session] 기본 세션 흐름"""
        # 세션 시작
        result = await call_tool("run_tool", {
            "cli_name": fast_session_bot,
            "message": "Hello Session",
            "session_id": "fast-session-001"
        })

        assert "response" in result
        assert "Hello Session" in result["response"]

    async def test_session_resume_flow(self, fast_session_bot):
        """[Session] 세션 재개 흐름"""
        # 세션 시작
        await call_tool("run_tool", {
            "cli_name": fast_session_bot,
            "message": "First message",
            "session_id": "fast-session-002"
        })

        # 세션 재개
        result = await call_tool("run_tool", {
            "cli_name": fast_session_bot,
            "message": "Second message",
            "session_id": "fast-session-002",
            "resume": True
        })

        assert "response" in result

    async def test_multiple_sessions_isolation(self, fast_session_bot):
        """[Session] 다중 세션 격리"""
        # 세션 A
        result_a = await call_tool("run_tool", {
            "cli_name": fast_session_bot,
            "message": "Session A",
            "session_id": "session-a"
        })

        # 세션 B
        result_b = await call_tool("run_tool", {
            "cli_name": fast_session_bot,
            "message": "Session B",
            "session_id": "session-b"
        })

        assert "response" in result_a
        assert "response" in result_b
        assert "Session A" in result_a["response"]
        assert "Session B" in result_b["response"]

    async def test_async_session(self, fast_session_bot):
        """[Session + Async] 비동기 세션"""
        result = await call_tool("run_tool", {
            "cli_name": fast_session_bot,
            "message": "Async in session",
            "session_id": "async-session-001",
            "run_async": True
        })

        assert "task_id" in result
        task_id = result["task_id"]

        # 폴링
        for _ in range(10):
            status = await call_tool("get_run_status", {"task_id": task_id})
            if status["status"] == "completed":
                assert "Async in session" in status["result"]
                return
            await asyncio.sleep(0.5)

        pytest.fail("Timeout waiting for async session task")
