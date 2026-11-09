from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel, Field
from c_dal_drivers import (
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
    name: str = Field(...,min_length=1,max_length=30)
    phone: str = Field(...,min_length=9,max_length=10)

class PatchDriver(BaseModel):
    name: Optional[str]                 = Field(None, min_length=1, max_length=30)
    phone: Optional[str]                = Field(None, min_length=9, max_length=11)
    status: Optional[str]               = Field(None, min_length=1, max_length=20)
    cartoons_count: Optional[int]       = Field(None, gt=0, lt=150)
    max_cartoons: Optional[int]         = Field(None, gt=0, lt=250)
    distribution_area: Optional[str]    = Field(None, min_length=1, max_length=20)

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
def get_existing_driver(driver_id: int):
    driver = get_driver(driver_id)
    if driver is None:
        raise HTTPException(status_code=404,detail="No driver found")
    return {
        'status': "Success",
        'driver': driver
    }

@drivers_router.post("/in")
def insert_new_driver(new_driver: NewDriver):
    inserted = insert_driver(d_name=new_driver.name, d_phone=new_driver.phone)
    if inserted is None:
        raise HTTPException(status_code=409,detail="Driver phone already exists")

    return {
        'status': "Success",
        'driver': inserted
    }

@drivers_router.patch("/patch/{driver_id}")
def patch_existing_driver(driver_id: int, driver: PatchDriver):
    existing_driver = get_driver(driver_id)
    if existing_driver is None:
        raise HTTPException(status_code=404,detail="No driver found")

    updated_driver = patch_driver(driver_id,d_name=driver.name, d_phone=driver.phone,
                                  d_cartoons_count=driver.cartoons_count,d_max_cartoons=driver.max_cartoons,
                                  d_distribution_area=driver.distribution_area,d_status=driver.status)
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

@drivers_router.delete("/del/{driver_id}")
def delete_existing_driver(driver_id: int):
    del_done = delete_driver(driver_id)
    if not del_done:
        raise HTTPException(status_code=404,detail="No driver found")
    return {
        'status': "Success"
    }







