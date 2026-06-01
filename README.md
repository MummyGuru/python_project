# 📦 WMS Practice System 
## Система управления складским учетом 
- Практический проект веб-приложения для управления складом. Система позволяет отслеживать товары, их категории, остатки на ячейках, регистрировать перемещения (приход, списание, перемещение) и создавать резервы. Проект реализован с использованием архитектуры REST API на FastAPI и клиентской части на чистом JS/HTML/CSS.
- Технологический стек
- Backend: Python 3.9+, FastAPI
- Database: MS SQL Server (через pyodbc)
- ORM: SQLAlchemy
- Auth: JWT (JSON Web Tokens), PyJWT, Passlib (Bcrypt)
- Frontend: HTML5, CSS3, Vanilla JavaScript (Single Page Application подход)
- Documentation: Swagger UI (автоматическая генерация)

## Структура проекта:
- ├── backend/
- │   ├── main.py              # Точка входа FastAPI, эндпоинты и роутинг
- │   ├── models.py            # Модели базы данных (SQLAlchemy)
- │   ├── schemas.py           # Pydantic схемы для валидации данных
- │   ├── database.py          # Настройки подключения к SQL Server
- │   └── utils/
- │       └── security.py      # Логика JWT, авторизации и хеширования паролей
- ├── frontend/
- │   ├── js/
- │   │   ├── app.js           # Основная бизнес-логика и работа с DOM
- │   │   ├── auth.js          # Логика авторизации, хранение токенов
- │   │   └── main.js          # Инициализация SPA, навигация
- │   ├── index.html           # Основной интерфейс (Dashboard)
- │   ├── login.html           # Страница авторизации
- │   ├── debug.html           # Отладочная страница для разработчиков
- │   └── static/
- │       └── style.css        # Глобальные стили
- ── gen_hash.py              # Утилита для генерации bcrypt-хешей паролей
- ├── requirements.txt         # Зависимости Python
- └── test_connection.py       # Скрипт проверки подключения к БД

## 🚀 Установка и запуск
1. Предварительные требования
Убедитесь, что у вас установлены:
Python 3.9+
MS SQL Server (Express или полная версия)
ODBC Driver 17 for SQL Server

2. Клонирование репозитория

```bash
git clone https://github.com/MummyGuru/python_project.git
cd python_project
```
3. Настройка зависимостей
Создайте виртуальное окружение (при необходимости) и установите библиотеки:
```bash
python -m venv venv
venv\Scripts\activate  # Для Windows
# source venv/bin/activate  # Для Linux/Mac

pip install fastapi uvicorn sqlalchemy pyodbc passlib[bcrypt] python-jose[cryptography] pyjwt python-multipart
```
4. Настройка базы данных
В файле backend/database.py проверьте настройки подключения.
По умолчанию используется:
Host: 127.0.0.1,1433
DB Name: WMS_Practice
Auth: Trusted Connection (Windows Authentication)

5. Запуск сервера
Перейдите в папку с бэкендом и запустите приложение:
```bash
cd backend
python main.py
```

Приложение станет доступно по адресу: http://localhost:8000

## 🔑 Аутентификация и Роли
Система поддерживает три уровня доступа. Для получения доступа к интерфейсу необходимо войти в систему.
Тестовые пользователи:
| Роль | Логин | Пароль | Описание доступа | 
| ---- | ----- | ------ | ---------------- |  
| Admin | admin | admin123 | Полный доступ, управление пользователями, создание товаров, закрытие периодов. Видит кнопку Swagger. | 
| Manager | manager | manager123 | Создание товаров, управление перемещениями и резервами. | 
| Warehouse | warehouse | warehouse123 | Просмотр остатков, проведение инвентаризации, чтение данных. | 

## 📚 API Документация (Swagger)
- Проект имеет встроенную интерактивную документацию.
- URL: http://localhost:8000/docs
- В интерфейсе некоторые кнопки и разделы скрыты в зависимости от вашей роли.
- Войдите под пользователем с ролью Admin:
  
  1. <img width="1293" height="586" alt="1" src="https://github.com/user-attachments/assets/b287dcf8-2120-422d-b448-23f8168a3735" />

  2. <img width="1306" height="210" alt="2" src="https://github.com/user-attachments/assets/f02074a2-5c30-48cf-b4c3-d183e37aa5c5" />

  3. <img width="602" height="338" alt="3" src="https://github.com/user-attachments/assets/456f2a3e-f1a3-4150-8bc2-dd0dbdaed3b8" />

## ⚠️ Известные ограничения и Roadmap
- Раздел "Резервы" (Reservations): Находится в стадии активной разработки. В текущей версии доступно создание резервов, но логика автоматического списания зарезервированного товара при отгрузке будет добавлена позже.
- Добавление товара: При создании товара с указанием начального количества, система автоматически создает Партию (Batch) и размещает остаток в первой доступной ячейке склада.
- Безопасность: В текущей версии используется Trusted_Connection для упрощения локального тестирования. Для продакшена рекомендуется настроить отдельного SQL-пользователя.
