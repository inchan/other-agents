"""동기 vs 비동기 처리 시나리오 테스트

pytest 통합 버전
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
async def test_bot():
    """테스트용 CLI 'test-bot' 추가"""
    await call_tool("add_agent", {
        "name": "test-bot",
        "command": "cat"
    })
    return "test-bot"


class TestSyncAsyncScenarios:
    """동기/비동기 처리 시나리오"""

    async def test_sync_basic_query(self, test_bot):
        """[Sync] 기본 단답형 질문 (즉시 응답)"""
        result = await call_tool("use_agent", {
            "cli_name": test_bot,
            "message": "Hello Sync",
            "run_async": False
        })

        assert "response" in result
        assert "Hello Sync" in result["response"]

    async def test_async_task_start(self, test_bot):
        """[Async] 비동기 작업 시작"""
        result = await call_tool("use_agent", {
            "cli_name": test_bot,
            "message": "Hello Async",
            "run_async": True
        })

        assert "task_id" in result
        assert result["status"] == "running"

    async def test_async_task_polling(self, test_bot):
        """[Async] 작업 상태 조회 (Polling)"""
        # 비동기 작업 시작
        result = await call_tool("use_agent", {
            "cli_name": test_bot,
            "message": "Hello Async Polling",
            "run_async": True
        })
        task_id = result["task_id"]

        # 폴링으로 완료 대기 (최적화: 0.05초 간격)
        for _ in range(40):
            status = await call_tool("get_task_status", {"task_id": task_id})
            if status["status"] == "completed":
                assert "Hello Async Polling" in status["result"]
                return
            await asyncio.sleep(0.05)

        pytest.fail("Timeout waiting for task")

    async def test_async_parallel_tasks(self, test_bot):
        """[Async] 병렬 작업 요청"""
        tasks = []
        for i in range(3):
            tasks.append(call_tool("use_agent", {
                "cli_name": test_bot,
                "message": f"Parallel {i}",
                "run_async": True
            }))

        results = await asyncio.gather(*tasks)

        assert len(results) == 3
        for r in results:
            assert "task_id" in r

    async def test_async_unknown_cli_error(self):
        """[Async] 존재하지 않는 CLI 에러 처리"""
        result = await call_tool("use_agent", {
            "cli_name": "unknown_bot",
            "message": "test",
            "run_async": True
        })
        task_id = result["task_id"]

        # 에러 상태 확인 (최적화: 0.1초 대기)
        await asyncio.sleep(0.1)
        status = await call_tool("get_task_status", {"task_id": task_id})

        assert status["status"] == "failed"
        assert "CLINotFoundError" in status["error"] or "알 수 없는 CLI" in status["error"]
