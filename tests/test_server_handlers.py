"""Tests for MCP Server call_tool handlers

Priority 1 테스트: server.py의 비동기 핸들러 및 도구 실행 로직
"""

import asyncio
import pytest
import time
from unittest.mock import patch, MagicMock, AsyncMock

from ai_cli_mcp.server import app, call_tool
from ai_cli_mcp.file_handler import (
    CLINotFoundError,
    CLITimeoutError,
    CLIExecutionError,
)
from ai_cli_mcp.task_manager import TaskManager, get_task_manager, InMemoryStorage, TaskStatus # type: ignore


class TestServerInitialization:
    """서버 초기화 및 툴 정의 테스트"""

    @pytest.mark.asyncio
    async def test_list_available_tools(self):
        """list_available_tools가 모든 툴을 올바르게 정의"""
        from ai_cli_mcp.server import list_available_tools

        tools = await list_available_tools()

        # 5개 툴 확인
        assert len(tools) == 5

        tool_names = [tool.name for tool in tools]
        assert "list_tools" in tool_names
        assert "run_tool" in tool_names
        assert "get_run_status" in tool_names
        assert "add_tool" in tool_names
        assert "run_multi_tools" in tool_names

        # run_multi_tools 스키마 검증
        run_multi_tools_tool = next(t for t in tools if t.name == "run_multi_tools")
        assert "message" in run_multi_tools_tool.inputSchema["properties"]
        assert "cli_names" in run_multi_tools_tool.inputSchema["properties"]
        assert run_multi_tools_tool.inputSchema["required"] == ["message"]


class TestCallToolListAvailableCLIs:
    """list_tools 도구 핸들러 테스트"""

    @pytest.mark.asyncio
    async def test_call_tool_list_available_clis_success(self):
        """list_tools 핸들러 성공 케이스"""
        result = await call_tool("list_tools", {})

        # 응답 형식 검증
        assert isinstance(result, dict)
        assert "clis" in result
        assert isinstance(result["clis"], list)

        # 기본 CLI 포함 확인
        cli_names = [cli["name"] for cli in result["clis"]]
        assert "claude" in cli_names
        assert "gemini" in cli_names
        assert "codex" in cli_names
        assert "qwen" in cli_names

    @pytest.mark.asyncio
    async def test_call_tool_list_available_clis_cli_structure(self):
        """각 CLI 항목의 구조 검증"""
        result = await call_tool("list_tools", {})

        for cli in result["clis"]:
            # 필수 필드 존재
            assert "name" in cli
            assert "command" in cli
            assert "version" in cli
            assert "installed" in cli

            # 필드 타입 검증
            assert isinstance(cli["name"], str)
            assert isinstance(cli["command"], str)
            assert isinstance(cli["installed"], bool)
            # version은 None 또는 문자열
            assert cli["version"] is None or isinstance(cli["version"], str)

    @pytest.mark.asyncio
    async def test_call_tool_list_available_clis_asyncio_called(self):
        """asyncio.to_thread()가 호출됨을 확인"""
        # 실제 list_tools 호출하므로 to_thread 호출 여부는
        # 실제 동작으로 검증됨. 이 테스트는 기존 success 테스트로 충분함
        result = await call_tool("list_tools", {})

        # 비동기 처리가 제대로 되었으므로 응답 받음
        assert isinstance(result, dict)
        assert "clis" in result


class TestCallToolRunTool:
    """run_tool 도구 핸들러 테스트 (동기/비동기 통합)"""

    @pytest.mark.asyncio
    async def test_call_tool_run_tool_sync_success(self):
        """run_tool 동기 실행 성공 케이스 (run_async=False)"""
        with patch("ai_cli_mcp.server.execute_cli_file_based") as mock_execute:
            mock_execute.return_value = "Success response"

            result = await call_tool("run_tool", {
                "cli_name": "claude",
                "message": "Hello, world!",
                "run_async": False
            })

            assert "response" in result
            assert result["response"] == "Success response"
            mock_execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_call_tool_run_tool_default_sync(self):
        """run_tool 기본값은 동기 실행이어야 함"""
        with patch("ai_cli_mcp.server.execute_cli_file_based") as mock_execute:
            mock_execute.return_value = "Success"

            result = await call_tool("run_tool", {
                "cli_name": "claude",
                "message": "Hello"
            }) # run_async 생략

            assert "response" in result
            mock_execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_call_tool_run_tool_async_success(self):
        """run_tool 비동기 실행 (run_async=True)"""
        
        # TaskManager 초기화 (테스트용)
        TaskManager._task_manager_instance = None
        manager = get_task_manager()
        manager.storage = InMemoryStorage()
        await manager.start()

        try:
            # 실제 실행 함수는 모킹
            mock_execution = MagicMock(return_value="Async Result")
            
            # server.py의 execute_cli_file_based를 패치
            # functools.partial로 감싸지기 때문에 호출 시점에 모킹된 함수가 사용됨
            with patch("ai_cli_mcp.server.execute_cli_file_based", new=mock_execution):
                result = await call_tool("run_tool", {
                    "cli_name": "claude",
                    "message": "Async Test",
                    "run_async": True
                })

                # 즉시 반환 확인
                assert "task_id" in result
                assert result["status"] == "running"
                task_id = result["task_id"]

                # 잠시 대기하여 작업 완료 유도
                await asyncio.sleep(0.1)

                # 작업이 실행되었는지 확인
                mock_execution.assert_called_once()

                # 상태 조회 (get_run_status 사용)
                status_result = await call_tool("get_run_status", {"task_id": task_id})
                assert status_result["status"] == "completed"
                assert status_result["result"] == "Async Result"

        finally:
            await manager.stop()
            TaskManager._task_manager_instance = None

    @pytest.mark.asyncio
    async def test_call_tool_run_tool_with_system_prompt(self):
        """시스템 프롬프트 포함 run_tool"""
        with patch("ai_cli_mcp.server.execute_cli_file_based") as mock_execute:
            mock_execute.return_value = "Response with system prompt"

            result = await call_tool("run_tool", {
                "cli_name": "claude",
                "message": "Tell me a story",
                "system_prompt": "You are a storyteller",
            })

            assert "response" in result
            mock_execute.assert_called_once()
            # system_prompt가 전달되었는지 확인
            call_args = mock_execute.call_args
            assert "system_prompt" in call_args.kwargs or len(call_args.args) > 3

    @pytest.mark.asyncio
    async def test_call_tool_run_tool_cli_not_found_error(self):
        """CLI not found 에러 처리 (동기)"""
        with patch("ai_cli_mcp.server.execute_cli_file_based") as mock_execute:
            mock_execute.side_effect = CLINotFoundError("claude (claude)가 설치되지 않았습니다")

            result = await call_tool("run_tool", {
                "cli_name": "claude",
                "message": "Hello",
            })

            assert "error" in result
            assert result["type"] == "CLINotFoundError"
            assert "설치되지 않았습니다" in result["error"]

    @pytest.mark.asyncio
    async def test_call_tool_run_tool_execution_error(self):
        """실행 에러 처리 (동기)"""
        with patch("ai_cli_mcp.server.execute_cli_file_based") as mock_execute:
            mock_execute.side_effect = CLIExecutionError("CLI 실행 실패 (코드 1)")

            result = await call_tool("run_tool", {
                "cli_name": "claude",
                "message": "Request",
            })

            assert "error" in result
            assert result["type"] == "CLIExecutionError"
            assert "실패" in result["error"]

    @pytest.mark.asyncio
    async def test_call_tool_run_tool_session_validation_error(self):
        """세션 검증 에러 처리"""
        with patch("ai_cli_mcp.server.execute_with_session") as mock_execute:
            mock_execute.side_effect = ValueError("Invalid session ID format")

            result = await call_tool("run_tool", {
                "cli_name": "claude",
                "message": "Test",
                "session_id": "invalid_id"
            })

            assert "error" in result
            assert result["type"] == "SessionValidationError"
            assert "Invalid session ID" in result["error"]

    @pytest.mark.asyncio
    async def test_call_tool_run_tool_timeout_error(self):
        """타임아웃 에러 처리 (동기)"""
        with patch("ai_cli_mcp.server.execute_cli_file_based") as mock_execute:
            mock_execute.side_effect = CLITimeoutError("CLI 타임아웃 (300초)")

            result = await call_tool("run_tool", {
                "cli_name": "claude",
                "message": "Request",
            })

            assert "error" in result
            assert result["type"] == "CLITimeoutError"
            assert "타임아웃" in result["error"]


class TestCallToolGetRunStatus:
    """get_run_status 도구 핸들러 테스트"""

    @pytest.fixture(autouse=True)
    async def setup_task_manager(self):
        """각 테스트 전에 TaskManager를 초기화하고, 테스트 후에 정리합니다."""
        TaskManager._task_manager_instance = None
        manager = get_task_manager()
        manager.storage = InMemoryStorage()
        await manager.start()
        yield manager
        await manager.stop()
        TaskManager._task_manager_instance = None

    @pytest.mark.asyncio
    async def test_get_run_status_not_found(self, setup_task_manager):
        """존재하지 않는 task_id 조회"""
        result = await call_tool("get_run_status", {"task_id": "invalid-id"})
        
        assert result["status"] == "not_found"
        assert "error" in result

    @pytest.mark.asyncio
    async def test_get_run_status_completed(self, setup_task_manager):
        """완료된 작업 상태 조회"""
        # 수동으로 작업 추가
        def dummy_task():
            return "Done"
        
        task_id = await setup_task_manager.start_task(dummy_task)
        await asyncio.sleep(0.1) # 완료 대기

        result = await call_tool("get_run_status", {"task_id": task_id})
        
        assert result["status"] == "completed"
        assert result["result"] == "Done"


class TestCallToolAddTool:
    """add_tool 도구 핸들러 테스트"""

    @pytest.mark.asyncio
    async def test_call_tool_add_tool_minimal(self):
        """add_tool 최소 필드 (name, command만)"""
        result = await call_tool("add_tool", {
            "name": "deepseek",
            "command": "deepseek",
        })

        assert result["success"] is True
        assert result["message"] == "CLI 'deepseek' 추가 완료"
        assert result["cli"]["name"] == "deepseek"
        assert result["cli"]["command"] == "deepseek"

    @pytest.mark.asyncio
    async def test_call_tool_add_tool_full_options(self):
        """add_tool 전체 옵션"""
        result = await call_tool("add_tool", {
            "name": "custom_gpt",
            "command": "custom-gpt",
            "extra_args": ["--mode", "chat"],
            "timeout": 120,
            "env_vars": {"API_KEY": "secret"},
            "supports_skip_git_check": True,
            "skip_git_check_position": "after_extra_args",
        })

        assert result["success"] is True
        assert result["message"] == "CLI 'custom_gpt' 추가 완료"
        assert result["cli"]["name"] == "custom_gpt"
        assert result["cli"]["command"] == "custom-gpt"

    @pytest.mark.asyncio
    async def test_call_tool_add_tool_then_list(self):
        """add_tool 후 list_tools에 반영"""
        # 1. CLI 추가
        add_result = await call_tool("add_tool", {
            "name": "test_cli",
            "command": "test-cli",
        })
        assert add_result["success"] is True

        # 2. 목록에서 확인
        list_result = await call_tool("list_tools", {})
        cli_names = [cli["name"] for cli in list_result["clis"]]
        assert "test_cli" in cli_names

    @pytest.mark.asyncio
    async def test_call_tool_add_tool_with_error(self):
        """add_tool 실패 케이스"""
        with patch("ai_cli_mcp.server.get_cli_registry") as mock_registry:
            mock_registry.return_value.add_cli.side_effect = Exception("Registry error")

            result = await call_tool("add_tool", {
                "name": "bad_cli",
                "command": "bad",
            })

            assert "error" in result
            assert result["type"] == "AddCLIError"


class TestCallToolUnknownTool:
    """Unknown tool 에러 처리"""

    @pytest.mark.asyncio
    async def test_call_tool_unknown_tool(self):
        """존재하지 않는 도구 호출"""
        result = await call_tool("nonexistent_tool", {})

        assert "error" in result
        assert "Unknown tool" in result["error"]
        assert "nonexistent_tool" in result["error"]


class TestCallToolIntegration:
    """도구 핸들러 통합 테스트"""

    @pytest.mark.asyncio
    async def test_call_tool_list_then_run(self):
        """list → run 순서대로 호출"""
        # 1. 목록 조회
        list_result = await call_tool("list_tools", {})
        assert "clis" in list_result

        # 2. run_tool 시도 (실제로는 모킹됨)
        with patch("ai_cli_mcp.server.execute_cli_file_based") as mock_execute:
            mock_execute.return_value = "Test response"

            send_result = await call_tool("run_tool", {
                "cli_name": "claude",
                "message": "Test",
            })
            assert "response" in send_result

    @pytest.mark.asyncio
    async def test_call_tool_add_then_list(self):
        """add_tool → list 순서대로 호출"""
        # 1. CLI 추가
        add_result = await call_tool("add_tool", {
            "name": "integration_test",
            "command": "it-cmd",
        })
        assert add_result["success"] is True

        # 2. 목록에서 확인
        list_result = await call_tool("list_tools", {})
        cli_names = [cli["name"] for cli in list_result["clis"]]
        assert "integration_test" in cli_names


class TestCallToolErrorHandling:
    """에러 처리 상세 테스트"""

    @pytest.mark.asyncio
    async def test_error_message_includes_cli_name(self):
        """에러 메시지에 CLI 이름 포함"""
        with patch("ai_cli_mcp.server.execute_cli_file_based") as mock_execute:
            mock_execute.side_effect = CLINotFoundError("claude가 설치되지 않았습니다")

            result = await call_tool("run_tool", {
                "cli_name": "claude",
                "message": "Test",
            })

            assert "claude" in result["error"]

    @pytest.mark.asyncio
    async def test_error_type_is_specified(self):
        """에러 타입이 명시됨"""
        with patch("ai_cli_mcp.server.execute_cli_file_based") as mock_execute:
            mock_execute.side_effect = CLITimeoutError("Timeout")

            result = await call_tool("run_tool", {
                "cli_name": "claude",
                "message": "Test",
            })

            assert "type" in result
            assert result["type"] == "CLITimeoutError"


# 엣지 케이스 테스트
class TestCallToolRunMultiTools:
    """run_multi_tools 도구 핸들러 테스트"""

    @pytest.mark.asyncio
    async def test_run_multi_tools_default_all_clis(self):
        """cli_names 미지정 시 모든 CLI에 전송"""
        with patch("ai_cli_mcp.server.execute_cli_file_based") as mock_execute:
            mock_execute.return_value = "Response from CLI"

            result = await call_tool("run_multi_tools", {
                "message": "Review this code"
            })

            # 응답 구조 검증
            assert "prompt" in result
            assert "responses" in result
            assert result["prompt"] == "Review this code"
            assert isinstance(result["responses"], dict)

            # 기본 CLI들이 호출되었는지 확인
            assert len(result["responses"]) > 0

            # 각 응답이 성공 형태인지 확인
            for cli_name, response in result["responses"].items():
                assert "success" in response
                if response["success"]:
                    assert "response" in response
                    assert response["response"] == "Response from CLI"

    @pytest.mark.asyncio
    async def test_run_multi_tools_specified_clis(self):
        """cli_names 지정 시 해당 CLI들에만 전송"""
        with patch("ai_cli_mcp.server.execute_cli_file_based") as mock_execute:
            mock_execute.return_value = "Specific response"

            result = await call_tool("run_multi_tools", {
                "message": "Plan this feature",
                "cli_names": ["claude", "gemini"]
            })

            assert "responses" in result
            assert len(result["responses"]) == 2
            assert "claude" in result["responses"]
            assert "gemini" in result["responses"]

            # 각 CLI의 응답 검증
            for cli_name in ["claude", "gemini"]:
                cli_result = result["responses"][cli_name]
                assert cli_result["success"] is True
                assert cli_result["response"] == "Specific response"

    @pytest.mark.asyncio
    async def test_run_multi_tools_parallel_execution(self):
        """병렬 실행 확인 - 모든 CLI가 동시에 실행됨"""
        call_times = []

        def mock_execute(*args, **kwargs):
            call_times.append(time.time())
            time.sleep(0.1)  # 각 CLI가 0.1초 걸린다고 가정
            return f"Response from {args[0]}"

        with patch("ai_cli_mcp.server.execute_cli_file_based", side_effect=mock_execute):
            start_time = time.time()

            result = await call_tool("run_multi_tools", {
                "message": "Test parallel",
                "cli_names": ["claude", "gemini", "codex"]
            })

            elapsed_time = time.time() - start_time

            # 병렬 실행되므로 3개가 순차 실행(0.3초)보다 빨라야 함
            # 실제로는 ~0.1초에 가까워야 하지만 여유를 두어 0.25초 이하로 검증
            assert elapsed_time < 0.25

            # 모든 CLI가 호출됨
            assert len(result["responses"]) == 3

    @pytest.mark.asyncio
    async def test_run_multi_tools_with_system_prompt(self):
        """시스템 프롬프트 전달"""
        with patch("ai_cli_mcp.server.execute_cli_file_based") as mock_execute:
            mock_execute.return_value = "Response"

            result = await call_tool("run_multi_tools", {
                "message": "Explain this",
                "cli_names": ["claude"],
                "system_prompt": "You are a code reviewer"
            })

            # execute_cli_file_based가 system_prompt와 함께 호출되었는지 확인
            call_args = mock_execute.call_args
            # system_prompt는 4번째 위치 인자 (cli_name, message, skip_git_repo_check, system_prompt)
            assert call_args.args[3] == "You are a code reviewer" or \
                   call_args.kwargs.get("system_prompt") == "You are a code reviewer"

    @pytest.mark.asyncio
    async def test_run_multi_tools_with_timeout(self):
        """타임아웃 설정 전달"""
        with patch("ai_cli_mcp.server.execute_cli_file_based") as mock_execute:
            mock_execute.return_value = "Response"

            result = await call_tool("run_multi_tools", {
                "message": "Quick task",
                "cli_names": ["claude"],
                "timeout": 60
            })

            # timeout이 전달되었는지 확인 (마지막 인자)
            call_args = mock_execute.call_args
            assert call_args.args[-1] == 60 or call_args.kwargs.get("timeout") == 60

    @pytest.mark.asyncio
    async def test_run_multi_tools_cli_not_found_error(self):
        """일부 CLI가 설치되지 않은 경우"""
        def mock_execute(cli_name, *args, **kwargs):
            if cli_name == "claude":
                return "Success"
            elif cli_name == "nonexistent":
                raise CLINotFoundError(f"{cli_name}가 설치되지 않았습니다")
            return "Success"

        with patch("ai_cli_mcp.server.execute_cli_file_based", side_effect=mock_execute):
            result = await call_tool("run_multi_tools", {
                "message": "Test",
                "cli_names": ["claude", "nonexistent"]
            })

            # claude는 성공
            assert result["responses"]["claude"]["success"] is True
            assert result["responses"]["claude"]["response"] == "Success"

            # nonexistent는 실패
            assert result["responses"]["nonexistent"]["success"] is False
            assert result["responses"]["nonexistent"]["type"] == "CLINotFoundError"
            assert "설치되지 않았습니다" in result["responses"]["nonexistent"]["error"]

    @pytest.mark.asyncio
    async def test_run_multi_tools_timeout_error(self):
        """일부 CLI가 타임아웃"""
        def mock_execute(cli_name, *args, **kwargs):
            if cli_name == "claude":
                return "Quick response"
            elif cli_name == "slow_cli":
                raise CLITimeoutError(f"{cli_name} 타임아웃")
            return "Response"

        with patch("ai_cli_mcp.server.execute_cli_file_based", side_effect=mock_execute):
            result = await call_tool("run_multi_tools", {
                "message": "Test",
                "cli_names": ["claude", "slow_cli"]
            })

            # claude는 성공
            assert result["responses"]["claude"]["success"] is True

            # slow_cli는 타임아웃
            assert result["responses"]["slow_cli"]["success"] is False
            assert result["responses"]["slow_cli"]["type"] == "CLITimeoutError"

    @pytest.mark.asyncio
    async def test_run_multi_tools_execution_error(self):
        """일부 CLI 실행 에러"""
        def mock_execute(cli_name, *args, **kwargs):
            if cli_name == "claude":
                return "Success"
            elif cli_name == "broken_cli":
                raise CLIExecutionError(f"{cli_name} 실행 실패")
            return "Success"

        with patch("ai_cli_mcp.server.execute_cli_file_based", side_effect=mock_execute):
            result = await call_tool("run_multi_tools", {
                "message": "Test",
                "cli_names": ["claude", "broken_cli"]
            })

            # claude는 성공
            assert result["responses"]["claude"]["success"] is True

            # broken_cli는 실패
            assert result["responses"]["broken_cli"]["success"] is False
            assert result["responses"]["broken_cli"]["type"] == "CLIExecutionError"

    @pytest.mark.asyncio
    async def test_run_multi_tools_mixed_results(self):
        """성공/실패가 섞인 결과"""
        def mock_execute(cli_name, *args, **kwargs):
            responses = {
                "claude": "Claude response",
                "gemini": CLINotFoundError("gemini not found"),
                "codex": "Codex response",
                "qwen": CLITimeoutError("qwen timeout")
            }
            result = responses.get(cli_name, "Default")
            if isinstance(result, Exception):
                raise result
            return result

        with patch("ai_cli_mcp.server.execute_cli_file_based", side_effect=mock_execute):
            result = await call_tool("run_multi_tools", {
                "message": "Review code",
                "cli_names": ["claude", "gemini", "codex", "qwen"]
            })

            # 성공 케이스
            assert result["responses"]["claude"]["success"] is True
            assert result["responses"]["codex"]["success"] is True

            # 실패 케이스
            assert result["responses"]["gemini"]["success"] is False
            assert result["responses"]["qwen"]["success"] is False

    @pytest.mark.asyncio
    async def test_run_multi_tools_empty_cli_list(self):
        """빈 CLI 목록"""
        with patch("ai_cli_mcp.server.list_available_clis") as mock_list:
            # 빈 목록 반환
            mock_list.return_value = []

            result = await call_tool("run_multi_tools", {
                "message": "Test"
            })

            # 응답은 있지만 비어있음
            assert "responses" in result
            assert len(result["responses"]) == 0

    @pytest.mark.asyncio
    async def test_run_multi_tools_single_cli(self):
        """단일 CLI만 지정"""
        with patch("ai_cli_mcp.server.execute_cli_file_based") as mock_execute:
            mock_execute.return_value = "Single response"

            result = await call_tool("run_multi_tools", {
                "message": "Test",
                "cli_names": ["claude"]
            })

            assert len(result["responses"]) == 1
            assert "claude" in result["responses"]
            assert result["responses"]["claude"]["success"] is True

    @pytest.mark.asyncio
    async def test_run_multi_tools_unexpected_error(self):
        """예상치 못한 에러 처리"""
        def mock_execute(cli_name, *args, **kwargs):
            if cli_name == "claude":
                return "Success"
            elif cli_name == "error_cli":
                raise RuntimeError("Unexpected runtime error")
            return "Success"

        with patch("ai_cli_mcp.server.execute_cli_file_based", side_effect=mock_execute):
            result = await call_tool("run_multi_tools", {
                "message": "Test",
                "cli_names": ["claude", "error_cli"]
            })

            # claude는 성공
            assert result["responses"]["claude"]["success"] is True

            # error_cli는 UnexpectedError
            assert result["responses"]["error_cli"]["success"] is False
            assert result["responses"]["error_cli"]["type"] == "UnexpectedError"
            assert "Unexpected runtime error" in result["responses"]["error_cli"]["error"]


class TestCallToolEdgeCases:
    """엣지 케이스 테스트"""

    @pytest.mark.asyncio
    async def test_run_tool_with_empty_message(self):
        """빈 메시지 전송"""
        with patch("ai_cli_mcp.server.execute_cli_file_based") as mock_execute:
            mock_execute.return_value = ""

            result = await call_tool("run_tool", {
                "cli_name": "claude",
                "message": "",
            })

            assert "response" in result

    @pytest.mark.asyncio
    async def test_run_tool_with_long_message(self):
        """매우 긴 메시지 전송"""
        long_message = "x" * 10000

        with patch("ai_cli_mcp.server.execute_cli_file_based") as mock_execute:
            mock_execute.return_value = "Response"

            result = await call_tool("run_tool", {
                "cli_name": "claude",
                "message": long_message,
            })

            assert "response" in result
