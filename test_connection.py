import pyodbc

# скрипт нужен для проверки соединения с базой данных

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=AN515-52\SQLEXPRESS;"
    "DATABASE=WMS_Practice;"
    "UID=AN515-52\sa;"
)

try:
    conn = pyodbc.connect(conn_str)
    print("✅ Подключение успешно!")
    conn.close()
except Exception as e:
    print(f"❌ Ошибка: {e}")