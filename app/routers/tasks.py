from __future__ import annotations

"""CRUD-роутер задач. Все задачи привязаны к текущему пользователю."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskOut, TaskUpdate

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


def _get_owned_task(task_id: int, db: Session, user: User) -> Task:
    task = db.get(Task, task_id)
    if task is None or task.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")
    return task


@router.get("", response_model=list[TaskOut])
def list_tasks(
    completed: bool | None = Query(default=None),
    search: str | None = Query(default=None, max_length=200),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Список задач текущего пользователя (фильтр по статусу и поиск по тексту)."""
    query = db.query(Task).filter(Task.owner_id == user.id)
    if completed is not None:
        query = query.filter(Task.completed == completed)
    if search:
        pattern = f"%{search.strip()}%"
        query = query.filter(
            Task.title.like(pattern) | Task.description.like(pattern)
        )
    return query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    data: TaskCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    task = Task(title=data.title.strip(), description=data.description, owner_id=user.id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/{task_id}", response_model=TaskOut)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return _get_owned_task(task_id, db, user)


@router.put("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    task = _get_owned_task(task_id, db, user)
    updates = data.model_dump(exclude_unset=True)
    if "title" in updates and not updates["title"].strip():
        raise HTTPException(status_code=422, detail="Название не может быть пустым")
    for field, value in updates.items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


@router.patch("/{task_id}/toggle", response_model=TaskOut)
def toggle_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Изменить статус задачи на противоположный."""
    task = _get_owned_task(task_id, db, user)
    task.completed = not task.completed
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    task = _get_owned_task(task_id, db, user)
    db.delete(task)
    db.commit()
