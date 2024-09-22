"""Enums."""

from enum import Enum


class EnvironmentName(Enum):
    """Environment name."""

    PROD: str = "prod"
    DEV: str = "dev"
