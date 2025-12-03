"""File Handler

파일 기반 CLI 실행 및 응답 처리
"""

import os
import subprocess
import tempfile
import uuid
from pathlib import Path

import yaml

from .cli_manager import is_cli_installed
from .cli_registry import get_cli_registry
from .logger import get_logger
from .session_manager import get_session_manager

logger = get_logger(__name__)


# Custom Exceptions
class CLINotFoundError(Exception):
    """CLI가 설치되지 않았을 때 발생"""
    pass


class CLITimeoutError(Exception):
    """CLI 실행이 타임아웃되었을 때 발생"""
    pass


class CLIExecutionError(Exception):
    """CLI 실행 중 에러 발생"""
    pass


def execute_cli_file_based(
    cli_name: str,
    message: str,
    skip_git_repo_check: bool = True,
    system_prompt: str = None,
    args: list[str] = None,
    timeout: int = None
) -> str:
    """
    파일 기반 CLI 실행 (시스템 프롬프트 및 args 지원)

    Process:
    1. 임시 input 파일 생성 (input_<uuid>.txt 또는 input_<uuid>.yaml)
    2. CLI 실행 (wrapped 모드 - cat input.txt | cli > output.txt)
    3. 임시 output 파일 읽기
    4. 임시 파일 정리

    Args:
        cli_name: CLI 이름 (claude, gemini, codex, qwen)
        message: 전송할 프롬프트
        skip_git_repo_check: Git 저장소 체크 건너뛰기 (Codex만 지원, 기본값: true)
        system_prompt: 시스템 프롬프트 (선택사항)
                      - Claude: --append-system-prompt 플래그로 처리
                      - 나머지: YAML 형식으로 input에 포함
        args: 추가 CLI 인자 (선택사항). 각 CLI가 지원하는 옵션만 전달됨
        timeout: 실행 타임아웃 (초, 선택사항). 제공 시 CLI 기본 설정을 덮어씀

    Returns:
        CLI 응답 문자열

    Raises:
        CLINotFoundError: CLI가 설치되지 않았을 때 발생
        CLITimeoutError: 실행 타임아웃
        CLIExecutionError: 실행 중 에러 발생
    """
    if args is None:
        args = []

    # 1. CLI 설정 가져오기 (Registry에서)
    registry = get_cli_registry()
    all_clis = registry.get_all_clis()

    if cli_name not in all_clis:
        raise CLINotFoundError(f"알 수 없는 CLI: {cli_name}")

    config = all_clis[cli_name]
    command = config["command"]
    # 요청별 타임아웃이 있으면 우선 사용, 없으면 설정값 사용
    execution_timeout = timeout if timeout is not None else config["timeout"]

    # 2. args 검증 및 필터링 (각 CLI별 지원 옵션 확인)
    validated_args = _validate_and_filter_args(cli_name, args, config)

    # 3. CLI 설치 확인
    if not is_cli_installed(command):
        raise CLINotFoundError(f"{cli_name} ({command})가 설치되지 않았습니다")

    # 4. 임시 파일 생성
    session_id = str(uuid.uuid4())
    input_fd, input_path = tempfile.mkstemp(
        suffix=".txt",
        prefix=f"ai_cli_mcp_input_{session_id}_",
        text=True
    )
    output_fd, output_path = tempfile.mkstemp(
        suffix=".txt",
        prefix=f"ai_cli_mcp_output_{session_id}_",
        text=True
    )

    try:
        # 4. input 파일에 메시지 작성
        with os.fdopen(input_fd, 'w') as f:
            if cli_name == "claude" and system_prompt:
                # Claude는 직접 stdin에 유저 프롬프트만 작성
                # (시스템 프롬프트는 --append-system-prompt 플래그로 처리)
                f.write(message)
            elif system_prompt:
                # 나머지 CLI: YAML 형식으로 시스템 프롬프트와 프롬프트 분리
                yaml_data = {
                    "system_prompt": system_prompt,
                    "prompt": message
                }
                yaml.dump(yaml_data, f, default_flow_style=False, allow_unicode=True)
            else:
                # 시스템 프롬프트 없음: 일반 메시지 작성
                f.write(message)

        # output_fd는 닫기 (subprocess가 쓸 수 있도록)
        os.close(output_fd)

        # 5. CLI 실행
        # cat input.txt | cli [extra_args] [validated_args] > output.txt
        result = _execute_cli(
            command=command,
            extra_args=config.get("extra_args", []),
            env_vars=config.get("env_vars", {}),
            input_path=input_path,
            output_path=output_path,
            timeout=execution_timeout,
            skip_git_repo_check=skip_git_repo_check,
            supports_skip_git_check=config.get("supports_skip_git_check", False),
            skip_git_check_position=config.get("skip_git_check_position", "before_extra_args"),
            cli_name=cli_name,
            system_prompt=system_prompt if cli_name == "claude" else None,
            additional_args=validated_args
        )

        # 6. output 파일 읽기
        with open(output_path, 'r') as f:
            response = f.read()

        return response

    finally:
        # 7. 임시 파일 정리
        _cleanup_temp_files(input_path, output_path)


def _execute_cli(
    command: str,
    extra_args: list,
    env_vars: dict[str, str],
    input_path: str,
    output_path: str,
    timeout: int,
    skip_git_repo_check: bool = True,
    supports_skip_git_check: bool = False,
    skip_git_check_position: str = "before_extra_args",
    cli_name: str = None,
    system_prompt: str = None,
    additional_args: list = None
) -> int:
    """
    CLI 실행 (환경 변수 설정 포함, 시스템 프롬프트 및 추가 인자 지원)

    Args:
        command: CLI 명령어
        extra_args: 추가 인자
        env_vars: 환경 변수
        input_path: 입력 파일 경로
        output_path: 출력 파일 경로
        timeout: 타임아웃 (초)
        skip_git_repo_check: Git 저장소 체크 건너뛰기 요청 (기본값: true)
        supports_skip_git_check: CLI가 --skip-git-repo-check 플래그를 지원하는지 여부
        skip_git_check_position: 플래그 위치 ("before_extra_args" 또는 "after_extra_args")
        cli_name: CLI 이름 (claude 감지용)
        system_prompt: 시스템 프롬프트 (Claude --append-system-prompt 플래그용)
        additional_args: 검증된 추가 CLI 인자

    Returns:
        리턴 코드

    Raises:
        CLITimeoutError
        CLIExecutionError
    """
    if additional_args is None:
        additional_args = []
    try:
        # 환경 변수 설정
        env = os.environ.copy()
        env.update(env_vars)

        # CLI 실행: input을 stdin으로, output을 파일로
        with open(input_path, 'r') as input_file:
            with open(output_path, 'w') as output_file:
                # 기본 명령어 구성
                full_command = [command]

                # Claude 특수 처리: --append-system-prompt 플래그 추가
                if cli_name == "claude" and system_prompt:
                    # Claude: --print --append-system-prompt "prompt" [stdin에서 message 읽기]
                    full_command.append("--print")
                    full_command.append("--append-system-prompt")
                    full_command.append(system_prompt)
                    logger.debug(f"Claude with system prompt: {full_command}")

                # skip_git_check_position에 따라 플래그 위치 결정
                if skip_git_repo_check and supports_skip_git_check:
                    if skip_git_check_position == "before_extra_args":
                        # codex --skip-git-repo-check exec - 형태
                        full_command.append("--skip-git-repo-check")
                        full_command.extend(extra_args)
                        logger.debug(f"Adding --skip-git-repo-check before extra_args: {full_command}")
                    else:  # after_extra_args
                        # codex exec --skip-git-repo-check - 형태
                        # extra_args를 분해해서 중간에 삽입
                        if len(extra_args) > 0:
                            full_command.append(extra_args[0])  # "exec"
                            full_command.append("--skip-git-repo-check")
                            full_command.extend(extra_args[1:])  # "-"
                            logger.debug(f"Adding --skip-git-repo-check after subcommand: {full_command}")
                        else:
                            full_command.append("--skip-git-repo-check")
                            logger.debug(f"Adding --skip-git-repo-check (no subcommand): {full_command}")
                else:
                    # skip 플래그 없이 일반 실행
                    full_command.extend(extra_args)

                # 검증된 추가 인자 추가
                full_command.extend(additional_args)

                result = subprocess.run(
                    full_command,
                    stdin=input_file,
                    stdout=output_file,
                    stderr=subprocess.PIPE,
                    timeout=timeout,
                    text=True,
                    env=env,  # 환경 변수 전달
                )

        # stderr 확인 (개선: stdout도 확인)
        if result.returncode != 0:
            error_msg = result.stderr or "알 수 없는 에러"
            logger.error(f"CLI 실행 실패 ({command}): {error_msg}")
            raise CLIExecutionError(
                f"CLI 실행 실패 (코드 {result.returncode}): {error_msg}"
            )

        logger.debug(f"CLI 실행 성공: {command}")

        return result.returncode

    except subprocess.TimeoutExpired as e:
        raise CLITimeoutError(f"CLI 실행 타임아웃 ({timeout}초)") from e
    except FileNotFoundError as e:
        raise CLINotFoundError(f"CLI 명령어를 찾을 수 없음: {command}") from e
    except Exception as e:
        raise CLIExecutionError(f"CLI 실행 중 에러: {str(e)}") from e


def _validate_and_filter_args(
    cli_name: str,
    args: list[str],
    config: dict
) -> list[str]:
    """
    CLI별 지원 옵션을 확인하고 args 검증 및 필터링

    Args:
        cli_name: CLI 이름
        args: 입력된 CLI 인자
        config: CLI 설정 (supported_args 포함)

    Returns:
        검증된 args (지원하지 않는 옵션은 제외)
    """
    supported_args = config.get("supported_args", [])

    if not args:
        return []

    if not supported_args:
        logger.warning(f"CLI '{cli_name}'에 지원하는 인자 목록이 없습니다. 입력된 args를 무시합니다: {args}")
        return []

    validated_args = []
    i = 0
    while i < len(args):
        arg = args[i]

        # 옵션 플래그 확인 (- 또는 --로 시작)
        if arg.startswith("-"):
            # 플래그가 지원되는지 확인
            if arg in supported_args:
                validated_args.append(arg)
                logger.debug(f"CLI '{cli_name}': 옵션 '{arg}' 허용됨")

                # 다음 인자가 값인지 확인 (플래그가 = 형식이 아니고, 다음 인자가 플래그가 아닌 경우)
                if not "=" in arg and i + 1 < len(args) and not args[i + 1].startswith("-"):
                    i += 1
                    validated_args.append(args[i])
                    logger.debug(f"CLI '{cli_name}': 옵션 값 '{args[i]}' 추가됨")
            else:
                logger.warning(f"CLI '{cli_name}': 지원하지 않는 옵션 '{arg}' 무시됨. (지원 옵션: {supported_args})")
        else:
            # 플래그가 아닌 경우 (값)
            if validated_args and not validated_args[-1].startswith("-"):
                # 이전 항목이 플래그가 아닌 경우, 단독 인자로 추가
                validated_args.append(arg)
            else:
                logger.debug(f"CLI '{cli_name}': 값 '{arg}' 추가됨")
                validated_args.append(arg)

        i += 1

    return validated_args


def _cleanup_temp_files(*file_paths: str) -> None:
    """임시 파일 정리"""
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"임시 파일 삭제: {file_path}")
        except Exception as e:
            logger.warning(f"임시 파일 삭제 실패: {file_path}, {e}")


def execute_with_session(
    cli_name: str,
    message: str,
    session_id: str,
    resume: bool = False,
    skip_git_repo_check: bool = True,
    system_prompt: str = None,
    args: list[str] = None,
    timeout: int = None
) -> str:
    """
    세션 모드로 CLI 실행

    Args:
        cli_name: CLI 이름
        message: 전송할 프롬프트
        session_id: 세션 ID (MCP 클라이언트 제공)
        resume: 기존 세션 재개 여부 (기본값: False)
        skip_git_repo_check: Git 저장소 체크 건너뛰기
        system_prompt: 시스템 프롬프트
        args: 추가 CLI 인자
        timeout: 타임아웃 초 (선택사항, None이면 CLI 기본값 사용)

    Returns:
        CLI 응답 문자열

    Raises:
        CLINotFoundError: CLI가 설치되지 않음
        CLITimeoutError: 실행 타임아웃
        CLIExecutionError: 실행 중 에러 발생
    """
    if args is None:
        args = []

    # 1. 세션 매니저에서 세션 정보 조회/생성
    session_manager = get_session_manager()
    session_info = session_manager.create_or_get_session(session_id, cli_name)

    # 2. CLI 설정 가져오기
    registry = get_cli_registry()
    all_clis = registry.get_all_clis()

    if cli_name not in all_clis:
        raise CLINotFoundError(f"알 수 없는 CLI: {cli_name}")

    config = all_clis[cli_name]
    command = config["command"]
    # timeout 우선순위: 파라미터 > CLI 기본값
    execution_timeout = timeout if timeout is not None else config["timeout"]

    # 3. CLI 설치 확인
    if not is_cli_installed(command):
        raise CLINotFoundError(f"{cli_name} ({command})가 설치되지 않았습니다")

    # 4. 세션 플래그 추가 (CLI별 전략)
    session_args = _build_session_args(
        cli_name=cli_name,
        cli_session_id=session_info.cli_session_id,
        resume=resume,
        is_first_request=(session_info.request_count == 1)
    )

    # 5. args와 session_args 병합
    combined_args = args + session_args

    # 6. args 검증 및 필터링
    validated_args = _validate_and_filter_args(cli_name, combined_args, config)

    # 7. 임시 파일 생성
    file_session_id = str(uuid.uuid4())
    input_fd, input_path = tempfile.mkstemp(
        suffix=".txt",
        prefix=f"ai_cli_mcp_input_{file_session_id}_",
        text=True
    )
    output_fd, output_path = tempfile.mkstemp(
        suffix=".txt",
        prefix=f"ai_cli_mcp_output_{file_session_id}_",
        text=True
    )

    try:
        # 8. input 파일에 메시지 작성
        with os.fdopen(input_fd, 'w') as f:
            if cli_name == "claude" and system_prompt:
                # Claude는 stdin에 유저 프롬프트만
                f.write(message)
            elif system_prompt:
                # 나머지 CLI: YAML 형식
                yaml_data = {
                    "system_prompt": system_prompt,
                    "prompt": message
                }
                yaml.dump(yaml_data, f, default_flow_style=False, allow_unicode=True)
            else:
                f.write(message)

        os.close(output_fd)

        # 9. CLI 실행
        result = _execute_cli(
            command=command,
            extra_args=config.get("extra_args", []),
            env_vars=config.get("env_vars", {}),
            input_path=input_path,
            output_path=output_path,
            timeout=execution_timeout,
            skip_git_repo_check=skip_git_repo_check,
            supports_skip_git_check=config.get("supports_skip_git_check", False),
            skip_git_check_position=config.get("skip_git_check_position", "before_extra_args"),
            cli_name=cli_name,
            system_prompt=system_prompt if cli_name == "claude" else None,
            additional_args=validated_args
        )

        # 10. output 파일 읽기
        with open(output_path, 'r') as f:
            response = f.read()

        return response

    finally:
        # 11. 임시 파일 정리
        _cleanup_temp_files(input_path, output_path)


def _build_session_args(
    cli_name: str,
    cli_session_id: str,
    resume: bool,
    is_first_request: bool
) -> list[str]:
    """
    CLI별 세션 플래그 생성

    Args:
        cli_name: CLI 이름
        cli_session_id: CLI용 세션 ID
        resume: 세션 재개 여부
        is_first_request: 첫 요청 여부

    Returns:
        세션 플래그 리스트
    """
    session_args = []

    if cli_name == "claude":
        # Claude: --session-id 또는 --resume 사용
        if resume and not is_first_request:
            # 세션 재개
            session_args.extend(["--resume", cli_session_id])
            logger.debug(f"Claude session resume: {cli_session_id}")
        else:
            # 새 세션 시작 (session_id 지정)
            session_args.extend(["--session-id", cli_session_id])
            logger.debug(f"Claude new session: {cli_session_id}")

    elif cli_name in ["gemini", "qwen"]:
        # Gemini/Qwen: 첫 요청이 아니면 --resume latest
        if not is_first_request and resume:
            session_args.extend(["--resume", "latest"])
            logger.debug(f"{cli_name} session resume: latest")
        else:
            logger.debug(f"{cli_name} new session (no flag)")

    elif cli_name == "codex":
        # Codex: resume 서브커맨드 사용 (첫 요청이 아닐 때)
        if not is_first_request and resume:
            # codex resume --last 형태
            # 주의: extra_args가 ["exec", "-"]인데 이를 ["resume", "--last"]로 변경해야 함
            # 이 부분은 _execute_cli에서 특수 처리 필요
            logger.warning("Codex session mode requires special handling in extra_args")
            # TODO: Codex 세션 모드 구현

    return session_args
