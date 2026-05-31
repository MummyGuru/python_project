from fastapi import FastAPI, HTTPException, Depends, status, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import models, schemas
from database import SessionLocal, engine, Base, get_db
from utils.security import (
    verify_password,
    create_access_token,
    get_password_hash,
    get_current_active_admin,
    get_current_user
)

# Создаем таблицы в БД
Base.metadata.create_all(bind=engine)

# ==================== ПРИЛОЖЕНИЕ ====================
app = FastAPI(
    title="WMS Practice API",
    version="0.1.0",
    description="Система учета складских операций",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== РОУТЕРЫ ====================
router = APIRouter()

@router.post("/api/login", response_model=schemas.TokenResponse, tags=["Auth"])
def login(credentials: schemas.Token, db: Session = Depends(get_db)):
    """Аутентификация пользователя и получение JWT токена"""
    user = db.query(models.User).filter(models.User.username == credentials.username).first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": schemas.UserOut.model_validate(user)
    }

@router.post("/api/register", status_code=status.HTTP_201_CREATED, tags=["Auth"])
def register(
    user_data: schemas.UserCreate, 
    db: Session = Depends(get_db),
    current_admin: models.User = Depends(get_current_active_admin)
):
    """Регистрация нового пользователя (только для админов)"""
    existing_user = db.query(models.User).filter(models.User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_user = models.User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {"message": "User created successfully", "username": db_user.username}

app.include_router(router)

# ==================== HEALTH CHECK ====================
@app.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

# ==================== PRODUCTS ====================
@app.get("/api/products", response_model=List[schemas.ProductOut], tags=["Products"])
def list_products(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Product).all()

@app.post("/api/products", response_model=schemas.ProductOut, tags=["Products"])
def create_product(
    product: schemas.ProductCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# ==================== MOVEMENTS ====================
@app.post("/api/movements", response_model=schemas.MovementOut, tags=["Movements"])
def create_movement(
    movement: schemas.MovementCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    product = db.query(models.Product).filter(models.Product.id == movement.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if movement.type == "receipt":
        product.quantity += movement.quantity
    elif movement.type == "writeoff":
        if product.quantity < movement.quantity:
            raise HTTPException(status_code=400, detail="Insufficient quantity")
        product.quantity -= movement.quantity

    db_movement = models.Movement(**movement.model_dump(), created_by=current_user.id, created_at=datetime.now())
    db.add(db_movement)
    db.commit()
    db.refresh(db_movement)
    return db_movement

# ==================== RESERVATIONS ====================
@app.post("/api/reservations", response_model=schemas.ReservationOut, tags=["Reservations"])
def create_reservation(
    reservation: schemas.ReservationCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    product = db.query(models.Product).filter(models.Product.id == reservation.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.quantity < reservation.quantity:
        raise HTTPException(status_code=400, detail="Insufficient quantity for reservation")

    db_reservation = models.Reservation(**reservation.model_dump(), created_by=current_user.id, created_at=datetime.now())
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation

# ==================== REPORTS ====================
@app.get("/api/reports/stock", tags=["Reports"])
def stock_report(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Отчет по складским остаткам"""
    products = db.query(models.Product).all()
    
    # Считаем общее количество из таблицы Stock
    total_quantity_result = db.query(func.sum(models.Stock.quantity)).scalar() or 0
    
    low_stock = []
    products_with_qty = []
    
    for product in products:
        product_qty = db.query(func.sum(models.Stock.quantity)).\
            join(models.Batch, models.Batch.id == models.Stock.batch_id).\
            filter(models.Batch.product_id == product.id).\
            scalar() or 0
        
        # Проверка на низкий остаток
        if product_qty < (product.min_stock or 0):
            low_stock.append({
                "id": product.id,
                "name": product.name,
                "quantity": product_qty,
                "min_stock": product.min_stock
            })
        
        products_with_qty.append({
            "id": product.id,
            "sku": product.sku,
            "name": product.name,
            "quantity": product_qty,
            "unit": product.unit,
            "min_stock": product.min_stock,
            "status": product.status,
            "price": product.price or 0
        })
    
    total_value = sum(p.get('price', 0) * p.get('quantity', 0) for p in products_with_qty)
    
    return {
        "total_products": len(products),
        "total_quantity": total_quantity_result,
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