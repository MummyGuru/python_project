from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from urllib.parse import quote_plus

# Настройки подключения к SQL Server
DB_HOST = os.getenv("DB_HOST", "127.0.0.1,1433")
DB_NAME = os.getenv("DB_NAME", "WMS_Practice")
DB_DRIVER = "ODBC+Driver+17+for+SQL+Server"
DB_USER = os.getenv("DB_USER", "gogi")
DB_PASSWORD = os.getenv("DB_PASSWORD", "110521")
password_encoded = quote_plus(DB_PASSWORD)

DATABASE_URL = f"mssql+pyodbc://{DB_USER}@{DB_HOST}/{DB_NAME}?driver={DB_DRIVER}&Trusted_Connection=yes"

# Создаём движок
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Проверка соединения перед использованием
    echo=True           # True для видимости вывода запросов в консоли
)

# SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

# Зависимость для FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()