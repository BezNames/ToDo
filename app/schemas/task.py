"""Pydantic-схемы задач."""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import Priority


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    priority: Priority = Priority.medium
    due_date: Optional[date] = None
    duration_minutes: Optional[int] = Field(default=None, ge=1, le=24 * 60)


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: Optional[bool] = None
    priority: Optional[Priority] = None
    due_date: Optional[date] = None
    duration_minutes: Optional[int] = Field(default=None, ge=1, le=24 * 60)


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str]
    completed: bool
    priority: Priority
    due_date: Optional[date]
    duration_minutes: Optional[int]
    created_at: datetime
    updated_at: datetime


class StatsOut(BaseModel):
    total: int
    active: int
    done: int
    overdue: int
    due_today: int
    planned_minutes: int
