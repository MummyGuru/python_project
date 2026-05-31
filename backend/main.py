from fastapi import FastAPI, HTTPException, Depends, status, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, date, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
import models, schemas
from database import SessionLocal, engine, Base, get_db

Base.metadata.create_all(bind=engine)

SECRET_KEY = "110521"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)

app = FastAPI(
    title="WMS Practice API",
    version="0.1.0",
    description="Система учета складских операций"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_role: str = payload.get("role")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def check_role(required_roles: List[str]):
    def role_checker(current_user: models.User = Depends(get_current_user)):
        if current_user.role not in required_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker

# ==================== AUTH ====================
@app.post("/api/login", response_model=schemas.TokenResponse)
def login(credentials: schemas.Token, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == credentials.username).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect credentials")
    
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": schemas.UserOut.model_validate(user)
    }

# ==================== CATEGORIES ====================
@app.get("/api/categories", response_model=List[schemas.CategoryOut], tags=["Categories"])
def list_categories(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Category).all()

# ==================== PRODUCTS ====================
@app.get("/api/products", response_model=List[schemas.ProductOut], tags=["Products"])
def list_products(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    products = db.query(models.Product).options(joinedload(models.Product.category)).all()
    return products

@app.post("/api/products", response_model=schemas.ProductOut, tags=["Products"])
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(check_role(["admin", "manager"]))
):
    product_data = product.model_dump(exclude={'initial_quantity'})
    
    db_product = models.Product(**product_data)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    if product.initial_quantity > 0:
        location = db.query(models.Location).first()
        if not location:
            db.delete(db_product)
            db.commit()
            raise HTTPException(status_code=400, detail="Невозможно создать остаток: в базе нет ни одной ячейки (Location).")

        new_batch = models.Batch(
            product_id=db_product.id,
            batch_number=f"MANUAL-{datetime.now().strftime('%Y%m%d')}",
            expiry_date=datetime(2099, 12, 31)
        )
        db.add(new_batch)
        db.commit()
        db.refresh(new_batch)

        new_stock = models.Stock(
            batch_id=new_batch.id,
            location_id=location.id,
            quantity=product.initial_quantity
        )
        db.add(new_stock)
        db.commit()

    return db_product

# ==================== STOCK/INVENTORY ====================
@app.get("/api/inventory", response_model=List[schemas.StockOut], tags=["Inventory"])
def get_inventory(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    stock_items = db.query(models.Stock).options(
        joinedload(models.Stock.batch).joinedload(models.Batch.product),
        joinedload(models.Stock.location)
    ).all()
    return stock_items

# ==================== MOVEMENTS ====================
@app.get("/api/movements", response_model=List[schemas.MovementOut], tags=["Movements"])
def list_movements(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    movements = db.query(models.Movement).options(
        joinedload(models.Movement.product),
        joinedload(models.Movement.batch)
    ).all()
    return movements

@app.post("/api/movements", response_model=schemas.MovementOut, tags=["Movements"])
def create_movement(
    movement: schemas.MovementCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(check_role(["admin", "manager", "warehouse"]))
):
    db_movement = models.Movement(
        **movement.model_dump(),
        created_by=current_user.id,
        created_at=datetime.now()
    )
    db.add(db_movement)
    db.commit()
    db.refresh(db_movement)
    return db_movement

# ==================== RESERVATIONS ====================
@app.get("/api/reservations", response_model=List[schemas.ReservationOut], tags=["Reservations"])
def list_reservations(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    from sqlalchemy.orm import joinedload
    return db.query(models.Reservation).options(
        joinedload(models.Reservation.product),
        joinedload(models.Reservation.batch)
    ).all()

@app.post("/api/reservations", response_model=schemas.ReservationOut, tags=["Reservations"])
def create_reservation(
    reservation: schemas.ReservationCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(check_role(["admin", "manager"]))
):
    db_reservation = models.Reservation(
        **reservation.model_dump(),
        created_by=current_user.id,
        created_at=datetime.now()
    )
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation

@app.delete("/api/reservations/{reservation_id}", tags=["Reservations"])
def delete_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(check_role(["admin", "manager", "warehouse"]))
):
    reservation = db.query(models.Reservation).filter(models.Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    
    db.delete(reservation)
    db.commit()
    return {"message": "Reservation cancelled"}

# ==================== REPORTS ====================
@app.get("/api/reports/stock", tags=["Reports"])
def stock_report(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Отчет по складским остаткам"""
    from sqlalchemy import func
    
    products = db.query(models.Product).all()
    
    stock_data = db.query(
        models.Batch.product_id,
        func.sum(models.Stock.quantity).label('total_qty')
    ).join(
        models.Stock, models.Stock.batch_id == models.Batch.id
    ).group_by(
        models.Batch.product_id
    ).all()
    
    product_quantities = {row.product_id: float(row.total_qty) if row.total_qty else 0 for row in stock_data}
    
    total_value = 0
    low_stock = []
    products_with_qty = []
    
    for product in products:
        qty = product_quantities.get(product.id, 0)
        price = float(product.price or 0)
        total_value += qty * price
        
        min_stock = float(product.min_stock or 0)
        if qty < min_stock:
            low_stock.append({
                "id": product.id,
                "name": product.name,
                "quantity": qty,
                "min_stock": min_stock
            })
        
        category_data = None
        if product.category:
            category_data = {
                "id": product.category.id,
                "name": product.category.name
            }
        
        products_with_qty.append({
            "id": product.id,
            "sku": product.sku,
            "name": product.name,
            "category_id": product.category_id,
            "category": category_data,
            "quantity": qty,
            "unit": product.unit,
            "min_stock": min_stock,
            "status": product.status,
            "price": price
        })
    
    return {
        "total_products": len(products),
        "total_quantity": sum(p["quantity"] for p in products_with_qty),
        "total_value": round(total_value, 2),
        "low_stock": low_stock,
        "products": products_with_qty
    }

# ==================== FRONTEND ====================
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/", include_in_schema=False)
def root():
    return FileResponse("frontend/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)