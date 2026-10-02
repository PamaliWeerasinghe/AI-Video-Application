"""Application configuration."""

from dataclasses import dataclass


@dataclass
class AppConfig:
    name: str = "AI Video Application"
