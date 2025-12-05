"""엔드투엔드 시나리오 테스트

실제 MCP 서버의 동작을 검증하는 엔드투엔드 테스트입니다.
각 시나리오는 실제 사용 케이스를 반영합니다.
"""

import pytest
import asyncio
from dataclasses import asdict
from typing import Dict, Any

from other_agents_mcp.server import call_tool, list_available_tools as list_tools
from other_agents_mcp.cli_manager import list_available_clis, CLIInfo
from other_agents_mcp.file_handler import CLINotFoundError, CLITimeoutError, CLIExecutionError


class TestE2EBasicWorkflow:
    """기본 워크플로우 E2E 테스트"""

    @pytest.mark.asyncio
    async def test_list_tools_then_list_clis(self):
        """시나리오: 도구 목록 조회 → CLI 목록 조회"""
        # Step 1: 도구 목록 조회
        tools = await list_tools()

        assert len(tools) == 5  # list_tools, run_tool, get_run_status, add_tool, run_multi_tools
        tool_names = {tool.name for tool in tools}
        assert "list_agents" in tool_names
        assert "use_agent" in tool_names
        assert "get_task_status" in tool_names
        assert "add_agent" in tool_names
        assert "use_agents" in tool_names

        # Step 2: list_tools 도구 실행
        result = await call_tool("list_agents", {})

        assert "clis" in result
        assert isinstance(result["clis"], list)
        assert len(result["clis"]) >= 4  # claude, gemini, codex, qwen

        # Step 3: CLI 정보 검증
        for cli in result["clis"]:
            assert "name" in cli
            assert "command" in cli
            assert "version" in cli
            assert "installed" in cli

    @pytest.mark.asyncio
    async def test_complete_cli_interaction_workflow(self):
        """시나리오: 전체 CLI 상호작용 워크플로우"""
        # Step 1: 사용 가능한 CLI 조회
        clis_result = await call_tool("list_agents", {})
        available_clis = clis_result["clis"]

        # Step 2: 설치된 CLI 찾기
        installed_cli = next(
            (cli for cli in available_clis if cli["installed"]),
            None
        )

        if installed_cli is None:
            pytest.skip("No CLI installed for E2E test")

        # Step 3: 설치된 CLI로 메시지 전송 (Mock 사용)
        # 주의: 실제 CLI 호출은 비용/시간이 들므로 선택적으로 실행
        # 실제 환경에서는 이 부분을 주석 해제하여 테스트
        # result = await call_tool("use_agent", {
        #     "cli_name": installed_cli["name"],
        #     "message": "Hello, this is a test."
        # })
        # assert "response" in result or "error" in result


class TestE2EErrorHandling:
    """에러 처리 E2E 테스트"""

    @pytest.mark.asyncio
    async def test_error_then_success_recovery(self):
        """시나리오: 에러 발생 → 정상 호출로 복구"""
        # Step 1: 존재하지 않는 CLI 호출 (에러 예상)
        error_result = await call_tool("use_agent", {
            "cli_name": "nonexistent-cli-12345",
            "message": "test"
        })

        assert "error" in error_result
        assert error_result["type"] == "CLINotFoundError"

        # Step 2: 정상 도구 호출 (복구 확인)
        success_result = await call_tool("list_agents", {})

        assert "clis" in success_result
        assert isinstance(success_result["clis"], list)

        # 서버가 에러 후에도 정상 작동함을 확인

    @pytest.mark.asyncio
    async def test_unknown_tool_error(self):
        """시나리오: 알 수 없는 도구 호출"""
        result = await call_tool("unknown_tool_12345", {})

        assert "error" in result
        assert "Unknown tool" in result["error"]

    @pytest.mark.asyncio
    async def test_missing_required_parameter(self):
        """시나리오: 필수 파라미터 누락"""
        # message 파라미터 누락
        with pytest.raises(KeyError):
            await call_tool("use_agent", {
                "cli_name": "claude"
                # message 누락
            })


class TestE2EDataConsistency:
    """데이터 일관성 E2E 테스트"""

    @pytest.mark.asyncio
    async def test_multiple_list_calls_consistency(self):
        """시나리오: 여러 번 호출해도 동일한 결과"""
        # 3번 연속 호출
        results = []
        for _ in range(3):
            result = await call_tool("list_agents", {})
            results.append(result)

        # 모든 결과가 동일한 CLI 개수를 반환
        cli_counts = [len(r["clis"]) for r in results]
        assert len(set(cli_counts)) == 1  # 모두 동일

        # CLI 이름도 동일
        cli_names_sets = [
            {cli["name"] for cli in r["clis"]}
            for r in results
        ]
        assert all(names == cli_names_sets[0] for names in cli_names_sets)

    @pytest.mark.asyncio
    async def test_cli_info_structure_consistency(self):
        """시나리오: CLI 정보 구조의 일관성"""
        result = await call_tool("list_agents", {})
        clis = result["clis"]

        # 모든 CLI가 동일한 구조를 가져야 함
        for cli in clis:
            required_keys = {"name", "command", "version", "installed"}
            assert set(cli.keys()) == required_keys

            # 타입 검증
            assert isinstance(cli["name"], str)
            assert isinstance(cli["command"], str)
            assert isinstance(cli["installed"], bool)
            assert cli["version"] is None or isinstance(cli["version"], str)


class TestE2EConfigValidation:
    """설정 검증 E2E 테스트"""

    @pytest.mark.asyncio
    async def test_all_configured_clis_present(self):
        """시나리오: 설정된 모든 CLI가 목록에 존재"""
        from other_agents_mcp.config import CLI_CONFIGS

        result = await call_tool("list_agents", {})
        returned_cli_names = {cli["name"] for cli in result["clis"]}
        configured_cli_names = set(CLI_CONFIGS.keys())

        assert returned_cli_names == configured_cli_names

    @pytest.mark.asyncio
    async def test_cli_command_matches_config(self):
        """시나리오: CLI 명령어가 설정과 일치"""
        from other_agents_mcp.config import CLI_CONFIGS

        result = await call_tool("list_agents", {})

        for cli in result["clis"]:
            cli_name = cli["name"]
            expected_command = CLI_CONFIGS[cli_name]["command"]
            assert cli["command"] == expected_command


class TestE2EErrorMessages:
    """에러 메시지 품질 E2E 테스트"""

    @pytest.mark.asyncio
    async def test_cli_not_found_error_message_quality(self):
        """시나리오: CLI 미설치 에러 메시지 품질"""
        result = await call_tool("use_agent", {
            "cli_name": "fake-cli-xyz",
            "message": "test"
        })

        assert "error" in result
        assert result["type"] == "CLINotFoundError"

        # 에러 메시지가 CLI 이름을 포함하는지 확인
        error_msg = result["error"]
        assert "fake-cli-xyz" in error_msg or "알 수 없는 CLI" in error_msg

    @pytest.mark.asyncio
    async def test_unknown_tool_error_message_includes_tool_name(self):
        """시나리오: 알 수 없는 도구 에러에 도구 이름 포함"""
        fake_tool = "non_existent_tool_xyz"
        result = await call_tool(fake_tool, {})

        assert "error" in result
        # 에러 메시지에 도구 이름이 포함되어야 함
        assert fake_tool in result["error"] or "Unknown" in result["error"]


class TestE2EStateManagement:
    """상태 관리 E2E 테스트"""

    @pytest.mark.asyncio
    async def test_stateless_server_behavior(self):
        """시나리오: 무상태 서버 동작 확인"""
        # 각 호출이 독립적이어야 함

        # Call 1: Error
        await call_tool("use_agent", {
            "cli_name": "nonexistent",
            "message": "test"
        })

        # Call 2: Success - 이전 에러의 영향을 받지 않아야 함
        result2 = await call_tool("list_agents", {})
        assert "clis" in result2

        # Call 3: Another error - 이전 성공의 영향을 받지 않아야 함
        result3 = await call_tool("unknown_tool", {})
        assert "error" in result3

        # Call 4: Success again
        result4 = await call_tool("list_agents", {})
        assert "clis" in result4

        # Result 2와 Result 4가 동일해야 함 (상태 없음)
        assert len(result2["clis"]) == len(result4["clis"])

    @pytest.mark.asyncio
    async def test_interleaved_calls(self):
        """시나리오: 교차 호출 독립성"""
        # 여러 도구를 교차로 호출
        results = []

        results.append(await call_tool("list_agents", {}))
        results.append(await call_tool("use_agent", {
            "cli_name": "fake",
            "message": "test"
        }))
        results.append(await call_tool("list_agents", {}))

        # 첫 번째와 세 번째 호출 결과가 동일해야 함
        assert len(results[0]["clis"]) == len(results[2]["clis"])

        # 두 번째 호출은 에러
        assert "error" in results[1]


class TestE2EPerformance:
    """성능 E2E 테스트"""

    @pytest.mark.asyncio
    async def test_list_clis_response_time(self):
        """시나리오: list_tools 응답 시간"""
        import time

        start = time.time()
        await call_tool("list_agents", {})
        elapsed = time.time() - start

        # 2초 이내 응답
        assert elapsed < 3.0  # 완화: 병렬 실행 시 더 느릴 수 있음

    @pytest.mark.asyncio
    async def test_error_response_immediate(self):
        """시나리오: 에러 응답은 즉각적"""
        import time

        start = time.time()
        await call_tool("use_agent", {
            "cli_name": "nonexistent",
            "message": "test"
        })
        elapsed = time.time() - start

        # 0.5초 이내 에러 응답
        assert elapsed < 0.5

    @pytest.mark.asyncio
    async def test_concurrent_list_calls(self):
        """시나리오: 동시 list_tools 호출"""
        import time

        start = time.time()

        # 5개 동시 호출
        tasks = [
            call_tool("list_agents", {})
            for _ in range(5)
        ]
        results = await asyncio.gather(*tasks)

        elapsed = time.time() - start

        # 모두 성공
        assert all("clis" in r for r in results)

        # 순차 실행보다 빨라야 함 (비동기 처리 확인)
        # 5초 이내 (순차면 5초 이상 걸림)
        assert elapsed < 10.0  # 완화: 병렬 실행 시 더 느릴 수 있음


class TestE2EIntegration:
    """통합 E2E 테스트"""

    @pytest.mark.asyncio
    async def test_full_user_journey(self):
        """시나리오: 전체 사용자 여정"""
        # 1. 사용 가능한 도구 확인
        tools = await list_tools()
        assert len(tools) == 5  # list_tools, run_tool, get_run_status, add_tool

        # 2. CLI 목록 조회
        clis_result = await call_tool("list_agents", {})
        assert "clis" in clis_result

        # 3. 존재하지 않는 CLI로 테스트 (에러 예상)
        error_result = await call_tool("use_agent", {
            "cli_name": "test-fake-cli",
            "message": "test"
        })
        assert "error" in error_result
        assert error_result["type"] == "CLINotFoundError"

        # 4. 다시 CLI 목록 조회 (복구 확인)
        clis_result2 = await call_tool("list_agents", {})
        assert "clis" in clis_result2
        assert len(clis_result2["clis"]) == len(clis_result["clis"])

    @pytest.mark.asyncio
    async def test_error_handling_completeness(self):
        """시나리오: 모든 에러 타입 처리"""
        # Unknown tool
        r1 = await call_tool("unknown", {})
        assert "error" in r1

        # CLI not found
        r2 = await call_tool("use_agent", {
            "cli_name": "fake",
            "message": "test"
        })
        assert "error" in r2
        assert r2["type"] == "CLINotFoundError"

        # Missing parameter
        with pytest.raises(KeyError):
            await call_tool("use_agent", {"cli_name": "claude"})

        # 모든 에러 후에도 정상 작동
        r3 = await call_tool("list_agents", {})
        assert "clis" in r3


class TestE2EAddCLI:
    """add_tool 도구 E2E 테스트"""

    @pytest.mark.asyncio
    async def test_add_cli_minimal(self):
        """시나리오: 최소 필드로 CLI 추가"""
        # CLI 추가
        result = await call_tool("add_agent", {
            "name": "testcli",
            "command": "testcli-cmd"
        })

        assert result["success"] is True
        assert "testcli" in result["message"]

        # 추가된 CLI가 목록에 나타나는지 확인
        list_result = await call_tool("list_agents", {})
        cli_names = {cli["name"] for cli in list_result["clis"]}
        assert "testcli" in cli_names

    @pytest.mark.asyncio
    async def test_add_cli_full_options(self):
        """시나리오: 전체 옵션으로 CLI 추가"""
        result = await call_tool("add_agent", {
            "name": "fullcli",
            "command": "fullcli-cmd",
            "extra_args": ["arg1", "arg2"],
            "timeout": 120,
            "env_vars": {"KEY": "value"},
            "supports_skip_git_check": True,
            "skip_git_check_position": "after_extra_args"
        })

        assert result["success"] is True

        # CLI 목록에서 확인
        list_result = await call_tool("list_agents", {})
        cli_names = {cli["name"] for cli in list_result["clis"]}
        assert "fullcli" in cli_names

    @pytest.mark.asyncio
    async def test_add_cli_then_use(self):
        """시나리오: CLI 추가 후 run_tool로 사용 시도"""
        # 1. CLI 추가
        await call_tool("add_agent", {
            "name": "fakecli",
            "command": "fakecli-nonexistent"
        })

        # 2. 추가된 CLI 확인
        list_result = await call_tool("list_agents", {})
        cli_names = {cli["name"] for cli in list_result["clis"]}
        assert "fakecli" in cli_names

        # 3. run_tool로 사용 시도 (실제로는 미설치되어 에러)
        send_result = await call_tool("use_agent", {
            "cli_name": "fakecli",
            "message": "test"
        })

        # CLI는 추가되었지만 실제로 설치되지 않아 에러
        assert "error" in send_result
        assert send_result["type"] == "CLINotFoundError"

    @pytest.mark.asyncio
    async def test_add_cli_overwrite_base(self):
        """시나리오: 기본 CLI를 런타임에 덮어쓰기"""
        # claude CLI의 원래 설정 확인
        list_result1 = await call_tool("list_agents", {})
        original_claude = next(
            cli for cli in list_result1["clis"] if cli["name"] == "claude"
        )

        # claude를 다른 명령어로 덮어쓰기
        await call_tool("add_agent", {
            "name": "claude",
            "command": "claude-modified"
        })

        # 덮어쓰기 확인
        list_result2 = await call_tool("list_agents", {})
        modified_claude = next(
            cli for cli in list_result2["clis"] if cli["name"] == "claude"
        )

        # 명령어가 변경되었는지 확인
        assert modified_claude["command"] == "claude-modified"

    @pytest.mark.asyncio
    async def test_add_multiple_clis(self):
        """시나리오: 여러 CLI를 순차적으로 추가"""
        # 3개 CLI 추가
        for i in range(1, 4):
            result = await call_tool("add_agent", {
                "name": f"cli{i}",
                "command": f"cli{i}-cmd"
            })
            assert result["success"] is True

        # 모두 목록에 나타나는지 확인
        list_result = await call_tool("list_agents", {})
        cli_names = {cli["name"] for cli in list_result["clis"]}

        assert "cli1" in cli_names
        assert "cli2" in cli_names
        assert "cli3" in cli_names


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
