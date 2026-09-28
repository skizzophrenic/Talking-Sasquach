"""Safe, non-destructive proximity game prototype."""

from .engine import GameEngine
from .models import AttackAlert, DeviceClass, NearbyDevice

__version__ = "0.2.0"

__all__ = ["AttackAlert", "DeviceClass", "GameEngine", "NearbyDevice"]
