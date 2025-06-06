from pydantic import BaseModel, Field, constr, condecimal
from typing import Optional, List

class StoreBase(BaseModel):
    name: constr(strip_whitespace=True, min_length=1)
    address: constr(strip_whitespace=True, min_length=1)

class StoreCreate(StoreBase):
    pass

class StoreUpdate(StoreBase):
    pass

class StoreOut(StoreBase):
    id: int
    class Config:
        orm_mode = True

class ProductBase(BaseModel):
    name: constr(strip_whitespace=True, min_length=1)
    price: float = Field(..., gt=0)

class ProductCreate(ProductBase):
    store_id: int

class ProductOut(ProductBase):
    id: int
    store_id: int
    class Config:
        orm_mode = True 