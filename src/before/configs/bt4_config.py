# configs/bt4_config.py

import json
from pathlib import Path
from typing import Dict


def get_bt4_config_path(config_name: str = "base_config.json") -> Path:
    """
    bt4 설정 파일의 경로를 반환

    Args:
        config_name: 설정 파일 이름

    Returns:
        Path: 설정 파일의 전체 경로
    """
    project_root = Path(__file__).parent.parent.parent
    config_path = project_root / "configs" / "bt4" / config_name

    if not config_path.exists():
        raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {config_path}")

    return config_path


def load_bt4_config(config_name: str = "base_config.json") -> Dict:
    """
    bt4 설정 파일을 로드

    Args:
        config_name: 설정 파일 이름

    Returns:
        Dict: 백테스트 설정
    """
    config_path = get_bt4_config_path(config_name)

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    return config


def get_base_bt4_config() -> Dict:
    """
    기본 bt4 설정을 반환

    Returns:
        Dict: 백테스트 기본 설정
    """
    return load_bt4_config("base_config.json")


def list_available_configs() -> list:
    """
    사용 가능한 모든 설정 파일 목록을 반환

    Returns:
        list: 설정 파일 이름 리스트
    """
    project_root = Path(__file__).parent.parent.parent
    config_dir = project_root / "configs" / "bt4"

    if not config_dir.exists():
        return []

    return [f.name for f in config_dir.glob("*.json")]
