from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from a_dal_stores import (
    get_store,
    get_store_table,
    insert_new_store,
    patch_store_table,
    delete_store,
    drop_stores_table,
    initial_stores
)


stores_router = APIRouter(
    prefix='/stores',
    tags=['stores']
)

class Store(BaseModel):
    store_number: int = Field(...,ge=0)
    store_name: str = Field(...,min_length=1,max_length=50)
    store_area: str = Field(...,min_length=1,max_length=20)

class StoreUpdate(BaseModel):
    store_name: Optional[str] = Field(None,min_length=1,max_length=50)
    store_area: Optional[str] = Field(None,min_length=1,max_length=20)

@stores_router.get('/')
def get_stores():
    stores = get_store_table()
    if stores is None:
        raise HTTPException(status_code=404, detail='Store not found')
    return {'status': 'Success',
            'stores': stores}

@stores_router.get('/{store_number}')
def get_exists_store(store_number: int):
    store = get_store(store_number)
    if store is None:
        raise HTTPException(status_code=404, detail='Store not found')
    return {'status': 'Success', 'store': store}


@stores_router.post('/in')
def insert_store(store: Store):
    store = insert_new_store(store_number_f=store.store_number,
                             store_name_f=store.store_name,
                             store_area_f=store.store_area)
    if store is None:
        raise HTTPException(status_code=409, detail='Store already exists')

    return {'status': 'Success', 'store': store}


@stores_router.patch('/patch/{store_number}')
def patch_store(store_number:int,update_store: StoreUpdate):
    existing_store = get_store(store_number)
    if existing_store is None:
        raise HTTPException(status_code=404, detail="No Store Number found")

    updated_store = patch_store_table(store_number=store_number,
                                      store_name=update_store.store_name,
                                      store_area=update_store.store_area)
    if updated_store == 0:
        raise HTTPException(status_code=400, detail="no parameter provided")

    if updated_store == 1:
        raise HTTPException(status_code=404, detail="Store not found")

    if updated_store == 2:
        raise HTTPException(status_code=409, detail="Store Failed to be inserted")

    return {'status': 'Success', 'store': updated_store}

# To Change number of store you should first delete store and after insert the updated store as new.


@stores_router.delete('/del/{store_number}')
def delete_existing_store(store_number: int):
    existing_store = get_store(store_number)
    if existing_store is None:
        raise HTTPException(status_code=404, detail='Store not found')
    done = delete_store(store_number=store_number)
    if not done:
        raise HTTPException(status_code=409, detail='Store could not be deleted')
    return {'status': 'Success', 'deleted_store': existing_store}

@stores_router.delete('/refresh')
def refresh_stores():
    re_done = drop_stores_table()
    if not re_done:
        raise HTTPException(status_code=404, detail='Failed to drop stores')

    initial_stores()
    return {'status': 'Success', 'refresh_stores': get_store_table()}




