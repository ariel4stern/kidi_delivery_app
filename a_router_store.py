from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
#from dal_stores import (
#    initial_stores,
#    get_store,
#    get_store_table,
#    insert_new_store,
#    patch_store_table,
#    delete_store,
#)


stores_router = APIRouter(
    prefix='/stores',
    tags=['stores']
)

class Store(BaseModel):
    store_number: int = Field(...,ge=0)
    store_name: str = Field(...,min_length=1,max_length=50)
    store_area: str = Field(...,min_length=1,max_length=20)

class StoreUpdate(BaseModel):
    up_store_name: Optional[str] = Field(...,min_length=1,max_length=50)
    up_store_area: Optional[str] = Field(...,min_length=1,max_length=20)

@stores_router.get('/get/{store_number}')
def get_exists_store(store_id: int):
    store = get_store(store_id)
    if store is None:
        raise HTTPException(status_code=404, detail='Store not found')
    return {'status': 'Success', 'store': store}

@stores_router.post('/post')
def insert_store(store: Store):
    store = insert_new_store(store_number_f=store.store_number,
                             store_name_f=store.store_name,
                             store_area_f=store.store_area)
    if store is None:
        raise HTTPException(status_code=409, detail='Store already exists')

    return {'status': 'Success', 'store': store}

@stores_router.patch('/patch/{store_number}')
def patch_store(store_number:int,update_store: StoreUpdate):
    store = get_store(store_number)
    if store is None:
        raise HTTPException(status_code=400, detail='No fields provided for update')

    updated_store = patch_store_table(store_number=store_number,
                                      store_name=update_store.up_store_name,
                                      store_area=update_store.up_store_area)

    if updated_store is None:
        raise HTTPException(status_code=409, detail='Store already exists')

    return {'status': 'Success', 'store': updated_store}

@stores_router.delete('/{store_number}')
def delete_existing_store(store_number: int):
    existing_store = get_store(store_number)
    if existing_store is None:
        raise HTTPException(status_code=404, detail='Store not found')
    done = delete_store(store_number=store_number)
    if not done:
        raise HTTPException(status_code=409, detail='Store could not be deleted')
    return {'status': 'Success', 'deleted_store': existing_store}





