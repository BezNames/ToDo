"""Перечисления для моделей."""
import enum


class Priority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
