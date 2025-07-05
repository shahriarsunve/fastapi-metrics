from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

# This must be present:
router = APIRouter()

class DataItem(BaseModel):
    id: int
    payload: dict

# In‑memory store
DATA_STORE: List[DataItem] = []

@router.get("", response_model=List[DataItem], summary="Retrieve all data items")
async def get_data():
    return DATA_STORE

@router.post("", response_model=DataItem, status_code=201, summary="Create a new data item")
async def create_data(item: DataItem):
    if any(existing.id == item.id for existing in DATA_STORE):
        raise HTTPException(status_code=400, detail="Item with this ID already exists")
    DATA_STORE.append(item)
    return item
