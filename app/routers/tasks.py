"""CRUD-роутер задач. Все задачи привязаны к текущему пользователю."""
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.enums import Priority
from app.models.task import Task
from app.models.user import User
from app.schemas.task import StatsOut, TaskCreate, TaskOut, TaskUpdate

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

# Порядок сортировки по приоритету: high -> medium -> low
_PRIORITY_ORDER = case(
    (Task.priority == Priority.high, 0),
    (Task.priority == Priority.medium, 1),
    else_=2,
)


def _get_owned_task(task_id: int, db: Session, user: User) -> Task:
    task = db.get(Task, task_id)
    if task is None or task.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")
    return task


@router.get("", response_model=List[TaskOut])
def list_tasks(
    completed: Optional[bool] = Query(default=None),
    search: Optional[str] = Query(default=None, max_length=200),
    priority: Optional[Priority] = Query(default=None),
    overdue: bool = Query(default=False, description="Только просроченные незавершённые"),
    sort: str = Query(default="created", pattern="^(created|priority|due)$"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Список задач текущего пользователя (фильтры, поиск, сортировка)."""
    query = db.query(Task).filter(Task.owner_id == user.id)
    if completed is not None:
        query = query.filter(Task.completed == completed)
    if search:
        pattern = f"%{search.strip()}%"
        query = query.filter(
            Task.title.like(pattern) | Task.description.like(pattern)
        )
    if priority:
        query = query.filter(Task.priority == priority)
    if overdue:
        query = query.filter(Task.completed == False, Task.due_date < date.today())  # noqa: E712

    if sort == "priority":
        query = query.order_by(_PRIORITY_ORDER, Task.created_at.desc())
    elif sort == "due":
        # задачи без срока — в конце
        query = query.order_by(
            Task.due_date.is_(None), Task.due_date.asc(), _PRIORITY_ORDER
        )
    else:
        query = query.order_by(Task.created_at.desc())
    return query.offset(skip).limit(limit).all()


@router.get("/stats", response_model=StatsOut)
def task_stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Сводка по задачам пользователя (считается по всем задачам, без фильтров)."""
    today = date.today()
    base = db.query(Task).filter(Task.owner_id == user.id)
    total = base.count()
    done = base.filter(Task.completed == True).count()  # noqa: E712
    active = total - done
    overdue = base.filter(
        Task.completed == False, Task.due_date.isnot(None), Task.due_date < today  # noqa: E712
    ).count()
    due_today = base.filter(
        Task.completed == False, Task.due_date == today  # noqa: E712
    ).count()
    planned_minutes = (
        db.query(func.coalesce(func.sum(Task.duration_minutes), 0))
        .filter(Task.owner_id == user.id, Task.completed == False)  # noqa: E712
        .scalar()
    )
    return StatsOut(
        total=total,
        active=active,
        done=done,
        overdue=overdue,
        due_today=due_today,
        planned_minutes=int(planned_minutes or 0),
    )


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    data: TaskCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    task = Task(
        title=data.title.strip(),
        description=data.description,
        priority=data.priority,
        due_date=data.due_date,
        duration_minutes=data.duration_minutes,
        owner_id=user.id,
    )
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
    if "title" in updates:
        if not updates["title"].strip():
            raise HTTPException(status_code=422, detail="Название не может быть пустым")
        updates["title"] = updates["title"].strip()
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


@router.delete("/done", status_code=status.HTTP_200_OK)
def delete_completed(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Удалить все выполненные задачи пользователя."""
    deleted = (
        db.query(Task)
        .filter(Task.owner_id == user.id, Task.completed == True)  # noqa: E712
        .delete()
    )
    db.commit()
    return {"deleted": deleted}


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    task = _get_owned_task(task_id, db, user)
    db.delete(task)
    db.commit()
