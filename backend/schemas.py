from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime, date
from typing import Optional, List

# ==================== USERS ====================
class UserBase(BaseModel):
    username: str
    role: str

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "warehouse"
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        if v not in ['admin', 'manager', 'warehouse']:
            raise ValueError('Role must be admin, manager, or warehouse')
        return v

class UserOut(BaseModel):
    id: int
    username: str
    role: str
    model_config = ConfigDict(from_attributes=True)

# ==================== AUTH ====================
class Token(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserOut

# ==================== CATEGORIES ====================
class CategoryBase(BaseModel):
    name: str

class CategoryOut(CategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# ==================== LOCATIONS ====================
class LocationBase(BaseModel):
    code: str
    name: Optional[str] = None

class LocationOut(LocationBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# ==================== PRODUCTS ====================
class ProductBase(BaseModel):
    sku: str
    name: str
    category_id: Optional[int] = None
    unit: str = "шт"
    min_stock: float = 0.0
    price: float = 0.0
    status: str = "active"

class ProductCreate(ProductBase):
    initial_quantity: float = 0.0 

class ProductOut(ProductBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# ==================== BATCHES ====================
class BatchBase(BaseModel):
    batch_number: str
    expiry_date: date
    product_id: int

class BatchOut(BatchBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# ==================== STOCK ====================
class StockBase(BaseModel):
    batch_id: int
    location_id: int
    quantity: float

class StockOut(StockBase):
    id: int
    batch: Optional[BatchOut] = None
    location: Optional[LocationOut] = None
    model_config = ConfigDict(from_attributes=True)

# ==================== MOVEMENTS ====================
class MovementBase(BaseModel):
    type: str
    product_id: int
    batch_id: int
    from_location_id: Optional[int] = None
    to_location_id: Optional[int] = None
    quantity: float = Field(gt=0)
    operation_date: date

class MovementCreate(MovementBase):
    pass

class MovementOut(MovementBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# ==================== RESERVATIONS ====================
class ReservationBase(BaseModel):
    product_id: int
    batch_id: int
    location_id: int
    quantity: float = Field(gt=0)
    expires_at: datetime

class ReservationCreate(ReservationBase):
    pass

class ReservationOut(ReservationBase):
    id: int
    status: str = "active"
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# ==================== INVENTORY ====================
class InventorySubmit(BaseModel):
    location_id: int
    check_date: date
    counted_quantities: dict[str, float]