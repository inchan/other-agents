"""CLI Manager

시스템에 설치된 CLI 감지 및 정보 조회
"""

import shutil
import subprocess
from dataclasses import dataclass
from typing import Optional

from .cli_registry import get_cli_registry
from .logger import get_logger

logger = get_logger(__name__)


@dataclass
class CLIInfo:
    """CLI 정보"""
    name: str
    command: str
    version: Optional[str]
    installed: bool


def is_cli_installed(command: str) -> bool:
    """
    CLI가 설치되어 있는지 확인

    Args:
        command: CLI 명령어 (예: "claude", "gemini")

    Returns:
        설치 여부 (True/False)
    """
    return shutil.which(command) is not None


def get_cli_version(command: str) -> Optional[str]:
    """
    CLI 버전 정보 조회

    Args:
        command: CLI 명령어

    Returns:
        버전 문자열 또는 None (조회 실패 시)
    """
    if not is_cli_installed(command):
        return None

    try:
        # --version 옵션으로 버전 정보 조회 시도
        result = subprocess.run(
            [command, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode == 0:
            # stdout 또는 stderr에서 버전 정보 추출
            version_output = result.stdout.strip() or result.stderr.strip()
            return version_output if version_output else None
        else:
            # --version이 실패하면 None 반환
            logger.debug(f"{command} --version 실패 (코드 {result.returncode})")
            return None

    except subprocess.TimeoutExpired:
        logger.warning(f"{command} --version 타임아웃")
        return None
    except FileNotFoundError:
        logger.debug(f"{command} 명령어를 찾을 수 없음")
        return None
    except Exception as e:
        logger.error(f"{command} 버전 조회 중 예외: {e}")
        return None


def list_available_clis() -> list[CLIInfo]:
    """
    설치된 CLI 목록 반환

    CLI Registry에서 모든 CLI를 조회하며,
    각 CLI의 설치 여부와 버전 정보를 조회합니다.

    Registry는 3단계 병합을 수행합니다:
    1. 기본 CLI (config.py)
    2. 파일 기반 (custom_clis.json)
    3. 런타임 추가 (add_cli 도구)

    Returns:
        CLIInfo 객체들의 리스트
    """
    registry = get_cli_registry()
    all_clis = registry.get_all_clis()

    clis = []

    for cli_name, config in all_clis.items():
        command = config["command"]
        installed = is_cli_installed(command)
        version = get_cli_version(command) if installed else None

        cli_info = CLIInfo(
            name=cli_name,
            command=command,
            version=version,
            installed=installed,
        )
        clis.append(cli_info)

    return clis
