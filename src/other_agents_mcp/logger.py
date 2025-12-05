"""Logging Configuration

로깅 설정 및 유틸리티
"""

import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """
    로거 인스턴스 생성

    Args:
        name: 로거 이름 (일반적으로 __name__)

    Returns:
        설정된 Logger 인스턴스
    """
    logger = logging.getLogger(name)

    # 이미 핸들러가 있으면 재사용
    if logger.handlers:
        return logger

    # 핸들러 설정
    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # 로그 레벨 설정 (환경 변수로 조정 가능)
    logger.setLevel(logging.INFO)

    return logger
