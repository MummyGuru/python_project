from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey, Text, Date, Boolean
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "Users"  # ← Исправлено: двойное подчёркивание
    id = Column("id", Integer, primary_key=True, index=True)
    username = Column("username", String(50), unique=True, nullable=False, index=True)
    password_hash = Column("password_hash", String(255), nullable=False)
    role = Column("role", String(20), nullable=False)

    # Relationships (имена должны точно совпадать с back_populates в других моделях)
    movements = relationship("Movement", back_populates="creator")
    reservations = relationship("Reservation", back_populates="creator")
    inventories = relationship("Inventory", back_populates="checker")

class Category(Base):
    __tablename__ = "Categories"
    id = Column("id", Integer, primary_key=True, index=True)
    name = Column("name", String(100), nullable=False)
    products = relationship("Product", back_populates="category")

class Location(Base):
    __tablename__ = "Locations"
    id = Column("id", Integer, primary_key=True, index=True)
    code = Column("code", String(20), unique=True, nullable=False)
    name = Column("name", String(100))
    stock = relationship("Stock", back_populates="location")

class Product(Base):
    __tablename__ = "Products"
    id = Column("id", Integer, primary_key=True, index=True)
    sku = Column("sku", String(30), unique=True, nullable=False)
    name = Column("name", String(100), nullable=False)
    category_id = Column("category_id", Integer, ForeignKey("Categories.id"), nullable=True)
    unit = Column("unit", String(20), nullable=False)
    min_stock = Column("min_stock", DECIMAL(10, 2), default=0)
    status = Column("status", String(20), default="active")
    price = Column("price", DECIMAL(10, 2), default=0)

    category = relationship("Category", back_populates="products")
    batches = relationship("Batch", back_populates="product")
    movements = relationship("Movement", back_populates="product")
    reservations = relationship("Reservation", back_populates="product")

class Batch(Base):
    __tablename__ = "Batches"
    id = Column("id", Integer, primary_key=True, index=True)
    product_id = Column("product_id", Integer, ForeignKey("Products.id"))
    batch_number = Column("batch_number", String(50), nullable=False)
    expiry_date = Column("expiry_date", Date, nullable=False)
    created_at = Column("created_at", DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="batches")
    stock = relationship("Stock", back_populates="batch")
    movements = relationship("Movement", back_populates="batch")
    reservations = relationship("Reservation", back_populates="batch")

class Stock(Base):
    __tablename__ = "Stock"
    id = Column("id", Integer, primary_key=True, index=True)
    batch_id = Column("batch_id", Integer, ForeignKey("Batches.id"))
    location_id = Column("location_id", Integer, ForeignKey("Locations.id"))
    quantity = Column("quantity", DECIMAL(10, 2), nullable=False, default=0)

    batch = relationship("Batch", back_populates="stock")
    location = relationship("Location", back_populates="stock")

class Movement(Base):
    __tablename__ = "Movements"
    id = Column("id", Integer, primary_key=True, index=True)
    type = Column("type", String(20), nullable=False)
    product_id = Column("product_id", Integer, ForeignKey("Products.id"))
    batch_id = Column("batch_id", Integer, ForeignKey("Batches.id"))
    from_location_id = Column("from_location_id", Integer, ForeignKey("Locations.id"))
    to_location_id = Column("to_location_id", Integer, ForeignKey("Locations.id"))
    quantity = Column("quantity", DECIMAL(10, 2), nullable=False)
    operation_date = Column("operation_date", Date, nullable=False)
    period_id = Column("period_id", Integer, ForeignKey("AccountingPeriods.id"))
    created_by = Column("created_by", Integer, ForeignKey("Users.id"))
    created_at = Column("created_at", DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="movements")
    batch = relationship("Batch", back_populates="movements")
    creator = relationship("User", back_populates="movements")  # ← Исправлено: совпадает с User.movements

class Reservation(Base):
    __tablename__ = "Reservations"
    id = Column("id", Integer, primary_key=True, index=True)
    product_id = Column("product_id", Integer, ForeignKey("Products.id"))
    batch_id = Column("batch_id", Integer, ForeignKey("Batches.id"))
    location_id = Column("location_id", Integer, ForeignKey("Locations.id"))
    quantity = Column("quantity", DECIMAL(10, 2), nullable=False)
    status = Column("status", String(20), default="active")
    expires_at = Column("expires_at", DateTime, nullable=False)
    created_by = Column("created_by", Integer, ForeignKey("Users.id"))

    product = relationship("Product", back_populates="reservations")
    batch = relationship("Batch", back_populates="reservations")
    creator = relationship("User", back_populates="reservations")  # ← Исправлено

class AccountingPeriod(Base):
    __tablename__ = "AccountingPeriods"
    id = Column("id", Integer, primary_key=True, index=True)
    year = Column("year", Integer, nullable=False)
    month = Column("month", Integer, nullable=False)
    is_closed = Column("is_closed", Boolean, default=False)

# Переименовано в Inventory, чтобы совпадало с main.py
class Inventory(Base):
    __tablename__ = "InventoryChecks"
    id = Column("id", Integer, primary_key=True, index=True)
    location_id = Column("location_id", Integer, ForeignKey("Locations.id"))
    product_id = Column("product_id", Integer, nullable=True)  # Добавлено для совместимости с main.py
    check_date = Column("check_date", Date, nullable=False)
    checked_by = Column("checked_by", Integer, ForeignKey("Users.id"))
    status = Column("status", String(20), default="pending")
    cell = Column("cell", String(50), nullable=True)  # Добавлено для совместимости с main.py

    checker = relationship("User", back_populates="inventories")  # ← Исправлено