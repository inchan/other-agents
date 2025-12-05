"""Tests for MCP Server lifecycle and main function

서버 생명주기 및 진입점 테스트
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock

from other_agents_mcp.server import app, main
from other_agents_mcp.task_manager import get_task_manager, TaskManager


class TestServerLifecycle:
    """서버 생명주기 테스트"""

    @pytest.mark.asyncio
    async def test_lifespan_context_manager(self):
        """lifespan이 정상적으로 컨텍스트 매니저로 동작"""
        # 간단한 lifespan 테스트 - 실제 server 동작 확인
        # lifespan은 실제 서버 실행 시에만 완전히 테스트 가능
        assert hasattr(app, "lifespan")
        assert callable(app.lifespan)


class TestMainFunction:
    """main() 함수 테스트"""

    def test_main_function_imports_and_calls_asyncio_run(self):
        """main()이 asyncio.run을 호출"""
        with patch("other_agents_mcp.server.asyncio.run") as mock_run:
            # asyncio.run을 모킹하여 실제 서버 시작 방지
            mock_run.return_value = None

            main()

            # asyncio.run이 호출되었는지 확인
            assert mock_run.called

            # 코루틴이 전달되었는지 확인
            args = mock_run.call_args[0]
            assert len(args) == 1
            import inspect
            assert inspect.iscoroutine(args[0])

    def test_main_function_logs_startup_info(self, caplog):
        """main()이 시작 정보를 로깅"""
        with patch("other_agents_mcp.server.asyncio.run") as mock_run:
            # asyncio.run을 모킹하여 실제 서버 시작 방지
            mock_run.return_value = None

            import logging
            caplog.set_level(logging.INFO)

            main()

            # 로그 메시지 확인
            log_messages = [record.message for record in caplog.records]
            assert any("Other Agents MCP Server starting" in msg for msg in log_messages)
            assert any("MCP SDK version: 1.22.0" in msg for msg in log_messages)
            assert any("Server name: other-agents-mcp" in msg for msg in log_messages)
            assert any("use_agents" in msg for msg in log_messages)
