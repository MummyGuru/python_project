from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey, Text, Date, Boolean
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)

    movements = relationship("Movement", back_populates="creator")
    reservations = relationship("Reservation", back_populates="creator")
    inventory_checks = relationship("InventoryCheck", back_populates="checker")

class Category(Base):
    __tablename__ = "Categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    products = relationship("Product", back_populates="category")

class Location(Base):
    __tablename__ = "Locations"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(100))
    stock = relationship("Stock", back_populates="location")

class Product(Base):
    __tablename__ = "Products"
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(30), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    category_id = Column(Integer, ForeignKey("Categories.id"), nullable=True)
    unit = Column(String(20), nullable=False, default="шт")
    min_stock = Column(DECIMAL(10, 2), default=0)
    price = Column(DECIMAL(10, 2), default=0)
    status = Column(String(20), default="active")

    category = relationship("Category", back_populates="products")
    batches = relationship("Batch", back_populates="product")
    movements = relationship("Movement", back_populates="product")
    reservations = relationship("Reservation", back_populates="product")

class Batch(Base):
    __tablename__ = "Batches"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("Products.id"))
    batch_number = Column(String(50), nullable=False)
    expiry_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="batches")
    stock = relationship("Stock", back_populates="batch")
    movements = relationship("Movement", back_populates="batch")
    reservations = relationship("Reservation", back_populates="batch")

class Stock(Base):
    __tablename__ = "Stock"
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("Batches.id"))
    location_id = Column(Integer, ForeignKey("Locations.id"))
    quantity = Column(DECIMAL(10, 2), nullable=False, default=0)

    batch = relationship("Batch", back_populates="stock")
    location = relationship("Location", back_populates="stock")

class Movement(Base):
    __tablename__ = "Movements"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(20), nullable=False)
    product_id = Column(Integer, ForeignKey("Products.id"))
    batch_id = Column(Integer, ForeignKey("Batches.id"))
    from_location_id = Column(Integer, ForeignKey("Locations.id"), nullable=True)
    to_location_id = Column(Integer, ForeignKey("Locations.id"), nullable=True)
    quantity = Column(DECIMAL(10, 2), nullable=False)
    operation_date = Column(Date, nullable=False)
    period_id = Column(Integer, ForeignKey("AccountingPeriods.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("Users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="movements")
    batch = relationship("Batch", back_populates="movements")
    creator = relationship("User", back_populates="movements")

class Reservation(Base):
    __tablename__ = "Reservations"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("Products.id"))
    batch_id = Column(Integer, ForeignKey("Batches.id"))
    location_id = Column(Integer, ForeignKey("Locations.id"))
    quantity = Column(DECIMAL(10, 2), nullable=False)
    status = Column(String(20), default="active")
    expires_at = Column(DateTime, nullable=False)
    created_by = Column(Integer, ForeignKey("Users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="reservations")
    batch = relationship("Batch", back_populates="reservations")
    creator = relationship("User", back_populates="reservations")

class AccountingPeriod(Base):
    __tablename__ = "AccountingPeriods"
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    is_closed = Column(Boolean, default=False)

class InventoryCheck(Base):
    __tablename__ = "InventoryChecks"
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("Locations.id"))
    check_date = Column(Date, nullable=False)
    checked_by = Column(Integer, ForeignKey("Users.id"))
    status = Column(String(20), default="pending")

    checker = relationship("User", back_populates="inventory_checks")