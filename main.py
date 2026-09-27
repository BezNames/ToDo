"""Точка входа FastAPI-приложения.

Запуск:  uvicorn main:app --reload --host 127.0.0.1 --port 8000
Docs:    http://localhost:8000/docs
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.routers import auth, tasks

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="ToDo API",
    description="Веб-версия ToDo (FastAPI + MySQL). Пароли — bcrypt-хэш с солью.",
    version="1.0.0",
)

# CORS — чтобы фронтенд (JS) мог обращаться к API с localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5500", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/", include_in_schema=False)
def root():
    """Главная страница — веб-приложение ToDo."""
    return FileResponse(BASE_DIR / "static" / "index.html")


# Статические файлы фронтенда (css/js)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/api/health", tags=["service"])
def health():
    return {"status": "ok"}
