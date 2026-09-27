-- Создание БД, пользователя MySQL и таблиц для ToDo-приложения.
-- Выполните: mysql -u root -p < init_db.sql
-- ИЛИ создайте таблицы автоматически (SQLAlchemy metadata) после запуска приложения.

CREATE DATABASE IF NOT EXISTS todo_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'todo_user'@'localhost' IDENTIFIED BY 'todo_pass';
GRANT ALL PRIVILEGES ON todo_db.* TO 'todo_user'@'localhost';
FLUSH PRIVILEGES;

USE todo_db;

CREATE TABLE IF NOT EXISTS users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    email         VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL COMMENT 'bcrypt-хэш с солью',
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS tasks (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    title       VARCHAR(200) NOT NULL,
    description TEXT NULL,
    completed   BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    owner_id    INT          NOT NULL,
    CONSTRAINT fk_tasks_owner
        FOREIGN KEY (owner_id) REFERENCES users (id) ON DELETE CASCADE,
    INDEX idx_tasks_owner (owner_id)
) ENGINE = InnoDB;
