"""Точка входа FastAPI-приложения.

Запуск:  uvicorn main:app --reload --host 127.0.0.1 --port 8000
Docs:    http://localhost:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, tasks

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


@app.get("/api/health", tags=["service"])
def health():
    return {"status": "ok"}
