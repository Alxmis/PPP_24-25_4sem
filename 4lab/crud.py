from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
import models, schemas

async def get_stores(db: AsyncSession):
    result = await db.execute(select(models.Store))
    return result.scalars().all()

async def create_store(db: AsyncSession, store: schemas.StoreCreate):
    db_store = models.Store(**store.dict())
    db.add(db_store)
    try:
        await db.commit()
        await db.refresh(db_store)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Store with this name and address already exists.")
    return db_store

async def update_store(db: AsyncSession, store_id: int, store: schemas.StoreUpdate):
    result = await db.execute(select(models.Store).where(models.Store.id == store_id))
    db_store = result.scalar_one_or_none()
    if not db_store:
        raise HTTPException(status_code=404, detail="Store not found.")
    db_store.name = store.name
    db_store.address = store.address
    try:
        await db.commit()
        await db.refresh(db_store)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Store with this name and address already exists.")
    return db_store

async def get_store_products(db: AsyncSession, store_id: int):
    result = await db.execute(select(models.Store).options(selectinload(models.Store.products)).where(models.Store.id == store_id))
    db_store = result.scalar_one_or_none()
    if not db_store:
        raise HTTPException(status_code=404, detail="Store not found.")
    return db_store.products

async def get_products(db: AsyncSession, store_id: int = None):
    query = select(models.Product)
    if store_id is not None:
        query = query.where(models.Product.store_id == store_id)
    result = await db.execute(query)
    return result.scalars().all()

async def create_product(db: AsyncSession, product: schemas.ProductCreate):
    # Проверяем, что магазин существует
    store = await db.get(models.Store, product.store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found.")
    db_product = models.Product(**product.dict())
    db.add(db_product)
    try:
        await db.commit()
        await db.refresh(db_product)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Product creation error.")
    return db_product

async def delete_product(db: AsyncSession, product_id: int):
    product = await db.get(models.Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    await db.delete(product)
    await db.commit() 