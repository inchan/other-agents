"""CLI Registry 테스트

4단계 CLI 로딩 및 병합 테스트
"""

import json
import os
import tempfile
from pathlib import Path

import pytest

from other_agents_mcp.cli_registry import CLIRegistry, get_cli_registry
from other_agents_mcp.config import CLI_CONFIGS


class TestCLIRegistry:
    """CLI Registry 테스트"""

    def setup_method(self):
        """테스트 전 초기화"""
        # 싱글톤 초기화
        CLIRegistry._instance = None
        # 환경 변수 정리
        if "CUSTOM_CLI_CONFIG" in os.environ:
            del os.environ["CUSTOM_CLI_CONFIG"]

    def test_singleton(self):
        """싱글톤 패턴 테스트"""
        registry1 = CLIRegistry()
        registry2 = CLIRegistry()
        assert registry1 is registry2

    def test_get_cli_registry(self):
        """get_cli_registry 헬퍼 함수 테스트"""
        registry = get_cli_registry()
        assert isinstance(registry, CLIRegistry)

    def test_get_all_clis_base_only(self):
        """기본 CLI만 로드 테스트"""
        registry = CLIRegistry()
        all_clis = registry.get_all_clis()

        # 기본 4개 CLI 존재 확인
        assert "claude" in all_clis
        assert "gemini" in all_clis
        assert "codex" in all_clis
        assert "qwen" in all_clis

        # config.py의 설정과 동일한지 확인
        assert all_clis["claude"] == CLI_CONFIGS["claude"]

    def test_add_cli_minimal(self):
        """add_cli 최소 필드 테스트 (name, command만)"""
        registry = CLIRegistry()
        registry.add_cli(name="testcli", command="testcli-cmd")

        all_clis = registry.get_all_clis()
        assert "testcli" in all_clis

        cli = all_clis["testcli"]
        assert cli["command"] == "testcli-cmd"
        assert cli["timeout"] == 300  # 기본값
        assert cli["extra_args"] == []  # 기본값
        assert cli["env_vars"] == {}  # 기본값
        assert cli["supports_skip_git_check"] is False  # 기본값
        assert cli["skip_git_check_position"] == "before_extra_args"  # 기본값

    def test_add_cli_full(self):
        """add_cli 전체 필드 테스트"""
        registry = CLIRegistry()
        registry.add_cli(
            name="fullcli",
            command="fullcli-cmd",
            extra_args=["arg1", "arg2"],
            timeout=120,
            env_vars={"KEY": "value"},
            supports_skip_git_check=True,
            skip_git_check_position="after_extra_args",
        )

        all_clis = registry.get_all_clis()
        cli = all_clis["fullcli"]

        assert cli["command"] == "fullcli-cmd"
        assert cli["extra_args"] == ["arg1", "arg2"]
        assert cli["timeout"] == 120
        assert cli["env_vars"] == {"KEY": "value"}
        assert cli["supports_skip_git_check"] is True
        assert cli["skip_git_check_position"] == "after_extra_args"

    def test_runtime_cli_priority_over_base(self):
        """런타임 CLI가 기본 CLI보다 우선순위 높음"""
        registry = CLIRegistry()

        # 기본 claude CLI의 timeout은 300
        base_claude = registry.get_all_clis()["claude"]
        assert base_claude["timeout"] == 300

        # 런타임에 claude 추가 (timeout 변경)
        registry.add_cli(
            name="claude",
            command="claude-modified",
            timeout=999
        )

        # 런타임 CLI가 우선
        all_clis = registry.get_all_clis()
        assert all_clis["claude"]["timeout"] == 999
        assert all_clis["claude"]["command"] == "claude-modified"

    def test_load_from_file(self, tmp_path):
        """custom_clis.json 파일에서 CLI 로드 테스트"""
        # 임시 custom_clis.json 생성
        custom_clis_json = {
            "filecli": {
                "command": "filecli-cmd",
                "timeout": 100
            }
        }

        # 프로젝트 루트에 custom_clis.json 생성
        project_root = Path(__file__).parent.parent
        custom_clis_path = project_root / "custom_clis.json"

        # 기존 파일 백업
        backup_content = None
        if custom_clis_path.exists():
            with open(custom_clis_path, "r") as f:
                backup_content = f.read()

        try:
            # 테스트용 파일 작성
            with open(custom_clis_path, "w") as f:
                json.dump(custom_clis_json, f)

            # 새 Registry 생성 (파일 읽기)
            CLIRegistry._instance = None
            registry = CLIRegistry()

            all_clis = registry.get_all_clis()
            assert "filecli" in all_clis
            assert all_clis["filecli"]["command"] == "filecli-cmd"
            assert all_clis["filecli"]["timeout"] == 100

        finally:
            # 백업 복원 또는 삭제
            if backup_content:
                with open(custom_clis_path, "w") as f:
                    f.write(backup_content)
            elif custom_clis_path.exists():
                custom_clis_path.unlink()

    def test_priority_runtime_over_file_over_base(self):
        """3단계 병합 우선순위 테스트"""
        # 1. 기본 CLI (claude)
        # 2. 파일로 claude 추가
        project_root = Path(__file__).parent.parent
        custom_clis_path = project_root / "custom_clis.json"

        backup_content = None
        if custom_clis_path.exists():
            with open(custom_clis_path, "r") as f:
                backup_content = f.read()

        try:
            with open(custom_clis_path, "w") as f:
                json.dump({"claude": {"command": "claude-file", "timeout": 222}}, f)

            # Registry 생성
            CLIRegistry._instance = None
            registry = CLIRegistry()

            # 파일 > 기본
            all_clis = registry.get_all_clis()
            assert all_clis["claude"]["timeout"] == 222

            # 3. 런타임으로 claude 추가
            registry.add_cli(name="claude", command="claude-runtime", timeout=333)

            # 런타임 > 파일 > 기본
            all_clis = registry.get_all_clis()
            assert all_clis["claude"]["timeout"] == 333
            assert all_clis["claude"]["command"] == "claude-runtime"

        finally:
            if backup_content:
                with open(custom_clis_path, "w") as f:
                    f.write(backup_content)
            elif custom_clis_path.exists():
                custom_clis_path.unlink()

    def test_apply_defaults(self):
        """_apply_defaults 메서드 테스트"""
        registry = CLIRegistry()

        # 최소 설정
        minimal_config = {"command": "test"}
        result = registry._apply_defaults(minimal_config)

        assert result["command"] == "test"
        assert result["timeout"] == 300
        assert result["extra_args"] == []
        assert result["env_vars"] == {}
        assert result["supports_skip_git_check"] is False
        assert result["skip_git_check_position"] == "before_extra_args"
