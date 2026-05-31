from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd.hash("warehouse123")  # ← заменить на нужный пароль
print(f"\n🔐 Ваш хеш:\n{hashed}\n")
input("Нажмите Enter, чтобы закрыть...")