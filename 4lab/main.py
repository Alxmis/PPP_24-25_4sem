from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from database import SessionLocal, engine, Base
import models, schemas, crud

app = FastAPI()

# Dependency
async def get_db():
    async with SessionLocal() as session:
        yield session

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Магазины
@app.get("/stores", response_model=List[schemas.StoreOut])
async def list_stores(db: AsyncSession = Depends(get_db)):
    return await crud.get_stores(db)

@app.post("/stores", response_model=schemas.StoreOut, status_code=201)
async def create_store(store: schemas.StoreCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_store(db, store)

@app.get("/stores/{store_id}/products", response_model=List[schemas.ProductOut])
async def get_store_products(store_id: int, db: AsyncSession = Depends(get_db)):
    return await crud.get_store_products(db, store_id)

@app.put("/stores/{store_id}", response_model=schemas.StoreOut)
async def update_store(store_id: int, store: schemas.StoreUpdate, db: AsyncSession = Depends(get_db)):
    return await crud.update_store(db, store_id, store)

# Товары
@app.get("/products", response_model=List[schemas.ProductOut])
async def list_products(store_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    return await crud.get_products(db, store_id)

@app.post("/products", response_model=schemas.ProductOut, status_code=201)
async def create_product(product: schemas.ProductCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_product(db, product)

@app.delete("/products/{product_id}", status_code=204)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    await crud.delete_product(db, product_id)
    return JSONResponse(status_code=204, content=None)

# Глобальный обработчик ошибок для возврата JSON
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

@app.exception_handler(422)
async def validation_exception_handler(request: Request, exc):
    return JSONResponse(status_code=422, content={"detail": exc.errors()}) 