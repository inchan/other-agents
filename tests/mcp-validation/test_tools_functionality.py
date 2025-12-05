"""MCP 도구 기능 테스트

list_available_clis와 send_message 도구의 실제 동작을 검증합니다.
Mock을 사용하여 외부 의존성을 제거하고 격리된 환경에서 테스트합니다.
"""

import pytest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import os
from dataclasses import asdict

from other_agents_mcp.server import call_tool
from other_agents_mcp.cli_manager import (
    list_available_clis,
    is_cli_installed,
    get_cli_version,
    CLIInfo
)
from other_agents_mcp.file_handler import (
    execute_cli_file_based,
    CLINotFoundError,
    CLIExecutionError,
    CLITimeoutError
)


class TestListAvailableCLIs:
    """list_available_clis 도구 기능 테스트"""

    def test_returns_list_of_cli_info(self):
        """CLIInfo 객체의 리스트를 반환하는지 확인"""
        result = list_available_clis()

        assert isinstance(result, list)
        assert len(result) > 0

        for cli_info in result:
            assert isinstance(cli_info, CLIInfo)

    def test_contains_all_configured_clis(self):
        """설정된 모든 CLI를 포함하는지 확인"""
        from other_agents_mcp.config import CLI_CONFIGS

        result = list_available_clis()
        cli_names = {cli.name for cli in result}

        for configured_cli in CLI_CONFIGS.keys():
            assert configured_cli in cli_names

    def test_cli_info_has_required_fields(self):
        """각 CLIInfo가 필수 필드를 가지는지 확인"""
        result = list_available_clis()

        for cli_info in result:
            assert hasattr(cli_info, 'name')
            assert hasattr(cli_info, 'command')
            assert hasattr(cli_info, 'version')
            assert hasattr(cli_info, 'installed')

            assert isinstance(cli_info.name, str)
            assert isinstance(cli_info.command, str)
            assert isinstance(cli_info.installed, bool)

    @patch('other_agents_mcp.cli_manager.is_cli_installed')
    def test_installed_flag_reflects_availability(self, mock_is_installed):
        """installed 플래그가 실제 설치 여부를 반영하는지 확인"""
        # 특정 CLI만 설치된 것으로 가정
        mock_is_installed.side_effect = lambda cmd: cmd == "claude"

        result = list_available_clis()

        for cli_info in result:
            if cli_info.command == "claude":
                assert cli_info.installed is True
            else:
                assert cli_info.installed is False

    @patch('other_agents_mcp.cli_manager.get_cli_version')
    @patch('other_agents_mcp.cli_manager.is_cli_installed')
    def test_version_populated_when_installed(self, mock_is_installed, mock_get_version):
        """설치된 CLI의 버전 정보가 조회되는지 확인"""
        mock_is_installed.return_value = True
        mock_get_version.return_value = "1.0.0"

        result = list_available_clis()

        for cli_info in result:
            assert cli_info.version == "1.0.0"

    @patch('other_agents_mcp.cli_manager.is_cli_installed')
    def test_version_none_when_not_installed(self, mock_is_installed):
        """설치되지 않은 CLI의 버전이 None인지 확인"""
        mock_is_installed.return_value = False

        result = list_available_clis()

        for cli_info in result:
            assert cli_info.version is None


class TestListToolsMCPTool:
    """list_tools MCP 도구 통합 테스트"""

    @pytest.mark.asyncio
    async def test_call_tool_returns_dict_with_clis_key(self):
        """call_tool이 'clis' 키를 가진 딕셔너리를 반환하는지 확인"""
        result = await call_tool("list_agents", {})

        assert isinstance(result, dict)
        assert "clis" in result

    @pytest.mark.asyncio
    async def test_clis_value_is_list_of_dicts(self):
        """clis 값이 딕셔너리의 리스트인지 확인"""
        result = await call_tool("list_agents", {})

        assert isinstance(result["clis"], list)

        for cli_dict in result["clis"]:
            assert isinstance(cli_dict, dict)
            assert "name" in cli_dict
            assert "command" in cli_dict
            assert "version" in cli_dict
            assert "installed" in cli_dict

    @pytest.mark.asyncio
    @patch('other_agents_mcp.server.list_available_clis')  # server.py에서 import한 것을 패치
    async def test_uses_asyncio_to_thread(self, mock_list_clis):
        """비동기 처리를 위해 asyncio.to_thread를 사용하는지 확인"""
        mock_cli = CLIInfo(
            name="test",
            command="test-cli",
            version="1.0.0",
            installed=True
        )
        mock_list_clis.return_value = [mock_cli]

        result = await call_tool("list_agents", {})

        # Mock이 호출되었는지 확인
        mock_list_clis.assert_called_once()

        # 결과가 올바르게 직렬화되었는지 확인
        assert result["clis"][0] == asdict(mock_cli)


class TestRunTool:
    """run_tool 도구 기능 테스트"""

    @pytest.mark.asyncio
    async def test_requires_cli_name_and_message(self):
        """cli_name과 message 파라미터가 필수인지 확인"""
        # 파라미터 없이 호출 시 KeyError 발생 예상
        with pytest.raises(KeyError):
            await call_tool("use_agent", {})

    @pytest.mark.asyncio
    @patch('other_agents_mcp.server.execute_cli_file_based')  # server.py에서 import한 것을 패치
    async def test_successful_message_send(self, mock_execute):
        """정상적인 메시지 전송 테스트"""
        mock_execute.return_value = "CLI response"

        result = await call_tool("use_agent", {
            "cli_name": "claude",
            "message": "Hello"
        })

        assert "response" in result
        assert result["response"] == "CLI response"
        mock_execute.assert_called_once_with("claude", "Hello", True, None, [], None)

    @pytest.mark.asyncio
    @patch('other_agents_mcp.server.execute_cli_file_based')  # server.py에서 import한 것을 패치
    async def test_cli_not_found_error(self, mock_execute):
        """CLI가 없을 때 에러 처리 확인"""
        mock_execute.side_effect = CLINotFoundError("CLI not found")

        result = await call_tool("use_agent", {
            "cli_name": "nonexistent",
            "message": "test"
        })

        assert "error" in result
        assert "type" in result
        assert result["type"] == "CLINotFoundError"

    @pytest.mark.asyncio
    @patch('other_agents_mcp.server.execute_cli_file_based')  # server.py에서 import한 것을 패치
    async def test_cli_timeout_error(self, mock_execute):
        """CLI 타임아웃 에러 처리 확인"""
        mock_execute.side_effect = CLITimeoutError("Timeout")

        result = await call_tool("use_agent", {
            "cli_name": "claude",
            "message": "test"
        })

        assert "error" in result
        assert result["type"] == "CLITimeoutError"

    @pytest.mark.asyncio
    @patch('other_agents_mcp.server.execute_cli_file_based')  # server.py에서 import한 것을 패치
    async def test_cli_execution_error(self, mock_execute):
        """CLI 실행 에러 처리 확인"""
        mock_execute.side_effect = CLIExecutionError("Execution failed")

        result = await call_tool("use_agent", {
            "cli_name": "claude",
            "message": "test"
        })

        assert "error" in result
        assert result["type"] == "CLIExecutionError"


class TestCLIManager:
    """CLI Manager 유틸리티 함수 테스트"""

    @patch('shutil.which')
    def test_is_cli_installed_true(self, mock_which):
        """CLI 설치 확인 - 설치됨"""
        mock_which.return_value = "/usr/local/bin/claude"

        result = is_cli_installed("claude")

        assert result is True
        mock_which.assert_called_once_with("claude")

    @patch('shutil.which')
    def test_is_cli_installed_false(self, mock_which):
        """CLI 설치 확인 - 미설치"""
        mock_which.return_value = None

        result = is_cli_installed("nonexistent")

        assert result is False

    @patch('other_agents_mcp.cli_manager.is_cli_installed')
    def test_get_cli_version_not_installed(self, mock_is_installed):
        """미설치 CLI의 버전 조회 시 None 반환"""
        mock_is_installed.return_value = False

        result = get_cli_version("nonexistent")

        assert result is None

    @patch('subprocess.run')
    @patch('other_agents_mcp.cli_manager.is_cli_installed')
    def test_get_cli_version_success(self, mock_is_installed, mock_run):
        """CLI 버전 조회 성공"""
        mock_is_installed.return_value = True
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="claude 1.0.0",
            stderr=""
        )

        result = get_cli_version("claude")

        assert result == "claude 1.0.0"

    @patch('subprocess.run')
    @patch('other_agents_mcp.cli_manager.is_cli_installed')
    def test_get_cli_version_timeout(self, mock_is_installed, mock_run):
        """버전 조회 타임아웃 시 None 반환"""
        import subprocess

        mock_is_installed.return_value = True
        mock_run.side_effect = subprocess.TimeoutExpired("claude", 5)

        result = get_cli_version("claude")

        assert result is None


class TestFileBasedCLIExecution:
    """파일 기반 CLI 실행 테스트"""

    @patch('other_agents_mcp.file_handler.is_cli_installed')
    def test_unknown_cli_raises_error(self, mock_is_installed):
        """알 수 없는 CLI 실행 시 CLINotFoundError 발생"""
        with pytest.raises(CLINotFoundError) as exc_info:
            execute_cli_file_based("unknown_cli", "test")

        assert "알 수 없는 CLI" in str(exc_info.value)

    @patch('other_agents_mcp.file_handler.is_cli_installed')
    def test_not_installed_cli_raises_error(self, mock_is_installed):
        """미설치 CLI 실행 시 CLINotFoundError 발생"""
        mock_is_installed.return_value = False

        with pytest.raises(CLINotFoundError) as exc_info:
            execute_cli_file_based("claude", "test")

        assert "설치되지 않았습니다" in str(exc_info.value)

    @patch('other_agents_mcp.file_handler._execute_cli')
    @patch('other_agents_mcp.file_handler.is_cli_installed')
    @patch('tempfile.mkstemp')
    def test_creates_temp_files(self, mock_mkstemp, mock_is_installed, mock_execute):
        """임시 파일이 생성되는지 확인"""
        # Setup
        mock_is_installed.return_value = True

        # 임시 파일 경로 생성
        input_fd = os.open(os.devnull, os.O_RDWR)
        output_fd = os.open(os.devnull, os.O_RDWR)

        mock_mkstemp.side_effect = [
            (input_fd, "/tmp/input.txt"),
            (output_fd, "/tmp/output.txt")
        ]

        mock_execute.return_value = 0

        # Mock open으로 파일 I/O 처리
        with patch('builtins.open', mock_open(read_data="response")):
            result = execute_cli_file_based("claude", "test message")

        # 임시 파일이 2번 생성되었는지 확인 (input, output)
        assert mock_mkstemp.call_count == 2
        assert result == "response"

    @patch('subprocess.run')
    @patch('other_agents_mcp.file_handler.is_cli_installed')
    @patch('builtins.open', new_callable=mock_open, read_data="CLI output")
    @patch('tempfile.mkstemp')
    def test_successful_execution(self, mock_mkstemp, mock_file, mock_is_installed, mock_run):
        """정상 실행 시 응답 반환"""
        # Setup
        mock_is_installed.return_value = True

        # 임시 파일 경로 설정
        with tempfile.NamedTemporaryFile(delete=False) as input_file:
            input_path = input_file.name
        with tempfile.NamedTemporaryFile(delete=False) as output_file:
            output_path = output_file.name

        try:
            mock_mkstemp.side_effect = [
                (os.open(input_path, os.O_RDWR), input_path),
                (os.open(output_path, os.O_RDWR), output_path)
            ]

            mock_run.return_value = MagicMock(
                returncode=0,
                stderr=""
            )

            # Execute
            result = execute_cli_file_based("claude", "test message")

            # Verify
            assert result == "CLI output"

        finally:
            # Cleanup
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)

    @patch('subprocess.run')
    @patch('other_agents_mcp.file_handler.is_cli_installed')
    def test_execution_timeout_raises_error(self, mock_is_installed, mock_run):
        """실행 타임아웃 시 CLITimeoutError 발생"""
        import subprocess

        mock_is_installed.return_value = True
        mock_run.side_effect = subprocess.TimeoutExpired("claude", 60)

        with pytest.raises(CLITimeoutError):
            execute_cli_file_based("claude", "test")

    @patch('other_agents_mcp.file_handler._cleanup_temp_files')
    @patch('other_agents_mcp.file_handler._execute_cli')
    @patch('other_agents_mcp.file_handler.is_cli_installed')
    @patch('tempfile.mkstemp')
    def test_temp_files_cleaned_up(self, mock_mkstemp, mock_is_installed,
                                   mock_execute, mock_cleanup):
        """임시 파일이 정리되는지 확인"""
        mock_is_installed.return_value = True

        input_fd = os.open(os.devnull, os.O_RDWR)
        output_fd = os.open(os.devnull, os.O_RDWR)

        mock_mkstemp.side_effect = [
            (input_fd, "/tmp/input.txt"),
            (output_fd, "/tmp/output.txt")
        ]

        mock_execute.return_value = 0

        with patch('builtins.open', mock_open(read_data="response")):
            execute_cli_file_based("claude", "test")

        # cleanup이 호출되었는지 확인
        mock_cleanup.assert_called_once()


class TestCLIConfiguration:
    """CLI 설정 테스트"""

    def test_all_clis_have_required_config(self):
        """모든 CLI가 필수 설정을 가지는지 확인"""
        from other_agents_mcp.config import CLI_CONFIGS

        for cli_name, config in CLI_CONFIGS.items():
            assert "command" in config
            assert "timeout" in config
            assert "extra_args" in config
            assert "env_vars" in config

            assert isinstance(config["command"], str)
            assert isinstance(config["timeout"], int)
            assert isinstance(config["extra_args"], list)
            assert isinstance(config["env_vars"], dict)

    def test_timeout_values_are_positive(self):
        """타임아웃 값이 양수인지 확인"""
        from other_agents_mcp.config import CLI_CONFIGS

        for cli_name, config in CLI_CONFIGS.items():
            assert config["timeout"] > 0

    def test_qwen_has_custom_env_vars(self):
        """qwen CLI가 커스텀 환경 변수를 가지는지 확인"""
        from other_agents_mcp.config import CLI_CONFIGS

        qwen_config = CLI_CONFIGS["qwen"]

        assert "OPENAI_BASE_URL" in qwen_config["env_vars"]
        assert "OPENAI_MODEL" in qwen_config["env_vars"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src/other_agents_mcp"])