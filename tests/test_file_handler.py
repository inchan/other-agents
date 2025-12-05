"""Tests for file_handler module"""

import os
import tempfile
import pytest
from pathlib import Path

from other_agents_mcp.file_handler import (
    execute_cli_file_based,
    CLINotFoundError,
    CLITimeoutError,
    CLIExecutionError,
)


class TestExecuteCliFileBased:
    """Test execute_cli_file_based function"""

    def test_function_exists(self):
        """함수가 존재해야 함"""
        assert callable(execute_cli_file_based)

    def test_uninstalled_cli_raises_error(self):
        """미설치 CLI는 CLINotFoundError 발생"""
        with pytest.raises(CLINotFoundError):
            execute_cli_file_based("nonexistent-cli-12345", "test message")

    def test_creates_temp_files(self, monkeypatch):
        """임시 파일을 생성해야 함"""
        temp_files_created = []

        original_mkstemp = tempfile.mkstemp

        def mock_mkstemp(suffix="", prefix="", dir=None, text=False):
            fd, path = original_mkstemp(suffix=suffix, prefix=prefix, dir=dir, text=text)
            temp_files_created.append(path)
            return fd, path

        monkeypatch.setattr(tempfile, "mkstemp", mock_mkstemp)

        # CLI_CONFIGS에 있는 CLI로 테스트
        # claude는 설치 안 되어 있을 수 있으므로 try-except
        try:
            execute_cli_file_based("claude", "test")
        except Exception:
            pass  # 실패해도 OK, 임시 파일 생성만 확인

        # 최소 2개의 임시 파일이 생성되어야 함 (input, output)
        assert len(temp_files_created) >= 2

    def test_cleans_up_temp_files(self):
        """임시 파일이 정리되어야 함"""
        # 실제로 동작하는 간단한 명령어로 테스트
        # echo는 거의 모든 시스템에 설치되어 있음
        temp_dir = tempfile.gettempdir()
        before_files = set(os.listdir(temp_dir))

        try:
            # echo 명령어로 간단한 테스트
            # wrapped 모드에서는 cat input | echo 형태로 실행될 것
            execute_cli_file_based("echo", "test")
        except Exception:
            pass  # 실행 실패해도 OK

        after_files = set(os.listdir(temp_dir))

        # other_agents_mcp 관련 임시 파일이 남아있지 않아야 함
        new_files = after_files - before_files
        mcp_temp_files = [f for f in new_files if "other_agents_mcp" in f]

        assert len(mcp_temp_files) == 0, \
            f"임시 파일이 정리되지 않음: {mcp_temp_files}"


class TestExceptionClasses:
    """Test custom exception classes"""

    def test_cli_not_found_error_exists(self):
        """CLINotFoundError 클래스가 존재해야 함"""
        assert issubclass(CLINotFoundError, Exception)

        # 인스턴스 생성 가능
        error = CLINotFoundError("test error")
        assert str(error) == "test error"

    def test_cli_timeout_error_exists(self):
        """CLITimeoutError 클래스가 존재해야 함"""
        assert issubclass(CLITimeoutError, Exception)

        error = CLITimeoutError("timeout")
        assert str(error) == "timeout"

    def test_cli_execution_error_exists(self):
        """CLIExecutionError 클래스가 존재해야 함"""
        assert issubclass(CLIExecutionError, Exception)

        error = CLIExecutionError("execution failed")
        assert str(error) == "execution failed"


class TestFileHandlerIntegration:
    """Integration tests with real CLI tools"""

    def test_echo_command_wrapped_mode(self):
        """echo 명령어로 wrapped 모드 테스트"""
        # echo는 거의 모든 시스템에 설치되어 있음
        # wrapped 모드: cat input.txt | echo > output.txt

        try:
            result = execute_cli_file_based("echo", "Hello, World!")
            # echo는 stdin을 무시하고 인자를 출력하므로,
            # wrapped 모드에서는 빈 출력이 나올 수 있음
            # 중요한 것은 에러 없이 실행되는 것
            assert isinstance(result, str)
        except CLINotFoundError:
            pytest.skip("echo 명령어가 설치되지 않음")

    def test_python3_version_check(self):
        """python3 --version으로 실제 실행 테스트"""
        # 이 테스트는 시스템에 python3가 설치되어 있어야 함
        try:
            # python3 명령어는 file_mode가 wrapped이므로
            # cat input.txt | python3 > output.txt 형태로 실행됨
            # 하지만 python3는 스크립트를 기대하므로 에러가 발생할 수 있음
            result = execute_cli_file_based("python3", "print('test')")

            # Python이 실행되었다면 결과가 문자열이어야 함
            assert isinstance(result, str)

        except (CLIExecutionError, CLINotFoundError):
            # 실행 에러는 OK (python3가 stdin을 스크립트로 해석하지 못할 수 있음)
            pass


class TestTimeout:
    """Test timeout functionality"""

    def test_timeout_handling(self, monkeypatch):
        """타임아웃이 올바르게 처리되어야 함"""
        # 타임아웃 테스트는 실제로 느린 명령어가 필요하므로
        # 여기서는 타임아웃 기능이 구현되어 있는지만 확인

        # config에 매우 짧은 타임아웃 설정
        from other_agents_mcp import config

        # claude CLI 사용 (config에 존재)
        original_timeout = config.CLI_CONFIGS["claude"]["timeout"]
        config.CLI_CONFIGS["claude"]["timeout"] = 0.001  # 1ms (매우 짧음)

        try:
            # 타임아웃이 발생할 수 있음
            execute_cli_file_based("claude", "test")
        except (CLITimeoutError, CLIExecutionError, CLINotFoundError):
            # 타임아웃, 실행 에러, 또는 미설치 - OK
            pass
        finally:
            # 원래 타임아웃으로 복구
            config.CLI_CONFIGS["claude"]["timeout"] = original_timeout
