from fastapi import APIRouter, HTTPException
from typing import List,Dict,Optional
from pydantic import BaseModel,Field
from d_dal_area import (
    get_all_dist_point,
    get_dist_point,
    insert_new_day,
    update_day_area,
    delete_day_area,
)
areas_router = APIRouter(
    tags=['areas'],
    prefix='/areas',
)

class Area(BaseModel):
    d_id : int = Field(...,gt=0,lt=10)
    day : str = Field(...,min_length=2,max_length=20)
    area : str = Field(...,min_length=2,max_length=20)

@areas_router.get('/')
def get_areas():
    d_point = get_all_dist_point()
    if d_point is None:
        raise HTTPException(status_code=404,detail='Table area_distributions not found')
    return {
        'status':'Success',
        'distribution_points':d_point
    }

@areas_router.get('/day_area')
def get_area_distribution(day:str,area:str):
    point = get_dist_point(day,area)
    if point is None:
        raise HTTPException(status_code=404,detail=f'{day,area} not found')
    return {
        'status':'Success',
        'distribution_point':point
    }

@areas_router.post('/in')
def insert_area(area:Area):
    inserted_dict = insert_new_day(d_id=area.d_id,
                                   day=area.day,
                                   area_dist=area.area)
    if insert_area is None:
        raise HTTPException(status_code=404,detail=f'problem inserting area {area.day},{area.area}')

    return {
        'status':'Success',
        'New distribution point':inserted_dict
    }

@areas_router.put('/up')
def update_area(area:Area):
    updated_area = update_day_area(d_id=area.d_id,
                                   day=area.day,
                                   area_dist=area.area)
    if updated_area is None:
        raise HTTPException(status_code=404,detail=f'{area.day},{area.area} not found')

    return {
        'status':'Success',
        'Updated distribution point':updated_area
    }

@areas_router.delete('/del')
def delete_area(day:str,area:str):
    deleted = delete_day_area(day,area)
    if not deleted:
        raise HTTPException(status_code=404,detail=f'{day},{area} not found')
    return {
        'status':'Success',
        'Deleted distribution point':deleted
    }

