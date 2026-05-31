from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime, date
from typing import Optional, List

# ==================== USERS ====================
class UserBase(BaseModel):
    username: str
    role: str

class UserCreate(UserBase):
    password: str
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        if v not in ['admin', 'manager', 'warehouse']:
            raise ValueError('Role must be admin, manager, or warehouse')
        return v

class UserOut(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# ==================== AUTH ====================
class Token(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserOut

# ==================== PRODUCTS ====================
class ProductBase(BaseModel):
    sku: str
    name: str
    category_id: Optional[int] = None
    unit: str = "шт"
    min_stock: float = 0.0
    status: str = "active"

class ProductCreate(ProductBase):
    pass

class ProductOut(ProductBase):
    id: int
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