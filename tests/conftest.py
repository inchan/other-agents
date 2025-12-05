"""Pytest 설정 파일

전역 fixture 및 테스트 설정
"""

import asyncio
import os
import pytest
from other_agents_mcp.cli_registry import CLIRegistry
from other_agents_mcp.task_manager import get_task_manager, TaskManager


@pytest.fixture
def reset_cli_registry():
    """각 테스트 전후로 CLI Registry 초기화

    싱글톤 패턴으로 인한 테스트 간 상태 공유를 방지합니다.
    최적화: autouse 제거, 필요한 테스트에만 명시적 적용
    """
    # 테스트 전: Registry 완전 초기화
    instance = CLIRegistry._instance
    if instance is not None:
        if hasattr(instance, "_initialized"):
            delattr(instance, "_initialized")
        if hasattr(instance, "_runtime_clis"):
            instance._runtime_clis = {}

    CLIRegistry._instance = None

    # 환경 변수 정리
    if "CUSTOM_CLI_CONFIG" in os.environ:
        del os.environ["CUSTOM_CLI_CONFIG"]

    yield

    # 테스트 후: 정리
    instance = CLIRegistry._instance
    if instance is not None:
        if hasattr(instance, "_initialized"):
            delattr(instance, "_initialized")
        if hasattr(instance, "_runtime_clis"):
            instance._runtime_clis = {}

    CLIRegistry._instance = None

    if "CUSTOM_CLI_CONFIG" in os.environ:
        del os.environ["CUSTOM_CLI_CONFIG"]


@pytest.fixture
async def task_manager_fixture():
    """각 테스트 전후로 TaskManager를 초기화하고 종료합니다."""
    # 테스트 시작 전: TaskManager 초기화 및 시작
    manager = get_task_manager()
    await manager.start()
    yield manager
    # 테스트 종료 후: TaskManager 중지
    await manager.stop()
    # 싱글톤 인스턴스 초기화
    TaskManager._task_manager_instance = None
