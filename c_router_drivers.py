from fastapi import APIRouter, HTTPException
from typing import Optional, List
from pydantic import BaseModel, Field
from a_dal_drivers import (
    get_driver,
    get_all_drivers,
    insert_driver,
    patch_driver,
    delete_driver
)
drivers_router = APIRouter(
    prefix="/drivers",
    tags=["drivers"]
)

class NewDriver(BaseModel):
    d_name: str = Field(...,min_length=1,max_length=30)
    d_phone: str = Field(...,min_length=9,max_length=11)

class UpdateDriver(BaseModel):
    d_name: Optional[str] = Field(None, min_length=1, max_length=30)
    d_phone: Optional[str] = Field(None, min_length=9, max_length=11)
    d_status: Optional[str] = Field('not_available', min_length=1, max_length=20)

@drivers_router.get("/")
def get_drivers():
    drivers_list = get_all_drivers()
    if drivers_list is None:
        raise HTTPException(status_code=404,detail="No drivers table found")

    return {
        'status': "Success",
        'drivers': drivers_list
    }

@drivers_router.get("/{driver_id}")
def get_driver(driver_id: int):
    driver = get_driver(driver_id)
    if driver is None:
        raise HTTPException(status_code=404,detail="No driver found")
    return {
        'status': "Success",
        'driver': driver
    }

@drivers_router.post("/")
def insert_new_driver(new_driver: NewDriver):
    inserted = insert_driver(d_name=new_driver.d_name, d_phone=new_driver.d_phone)
    if inserted is None:
        raise HTTPException(status_code=409,detail="Driver already exists")

    return {
        'status': "Success",
        'driver': inserted
    }

@drivers_router.patch("/{driver_id}")
def patch_existing_driver(driver_id: int, driver: UpdateDriver):
    existing_driver = get_driver(driver_id)
    if existing_driver is None:
        raise HTTPException(status_code=404,detail="No driver found")

    updated_driver = patch_driver(driver_id,d_name=driver.d_name, d_phone=driver.d_phone, d_status=driver.d_status)
    if updated_driver == 0:
        raise HTTPException(status_code=400,detail="no parameter provided")

    if updated_driver == 1:
        raise HTTPException(status_code=404, detail="Driver not found")

    if updated_driver == 2:
        raise HTTPException(status_code=409,detail="Driver data conflicts with existing data")

    return {
        'status': "Success",
        'driver': updated_driver
    }

@drivers_router.delete("/{driver_id}")
def delete_existing_driver(driver_id: int):
    del_done = delete_driver(driver_id)
    if not del_done:
        raise HTTPException(status_code=404,detail="No driver found")
    return {
        'status': "Success"
    }







