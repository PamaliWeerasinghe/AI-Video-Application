"""Application state definitions."""

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class AppState:
    data: Dict[str, Any] = field(default_factory=dict)
