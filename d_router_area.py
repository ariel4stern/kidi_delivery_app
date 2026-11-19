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

class Point(BaseModel):
    d_id : Optional[int] = Field(None,gt=0,lt=10)
    day : str = Field(...,min_length=2,max_length=20)
    point : int = Field(0,gt=0)

class UpdatePoint(BaseModel):
    d_id : int = Field(...,gt=0,lt=10)
    day : str = Field(...,min_length=2,max_length=20)
    point : int = Field(...,gt=0)

@areas_router.get('/')
def get_points():
    d_point = get_all_dist_point()
    if d_point is None:
        raise HTTPException(status_code=404,detail='Table area_distributions not found')
    return {
        'status':'Success',
        'distribution_points':d_point
    }

# request format: http://127.0.0.1:{{port}}/areas/day_point?day=sunday&point=1
@areas_router.get('/day_point')
def get_area_distribution(day:str,point:int):
    selected_point = get_dist_point(day,point)
    if selected_point is None:
        raise HTTPException(status_code=404,detail=f'{day,point} not found')
    return {
        'status':'Success',
        'distribution_point':selected_point
    }

@areas_router.post('/day_point/in')
def insert_area(p:Point):
    inserted_dict = insert_new_day(d_id=p.d_id,
                                   day=p.day,
                                   point=p.point)
    if inserted_dict is None:
        raise HTTPException(status_code=404,detail=f'problem inserting area {p.day},{p.point}')

    return {
        'status':'Success',
        'New distribution point':inserted_dict
    }

@areas_router.put('/day_point/up')
def update_area(p:UpdatePoint):
    updated_area = update_day_area(d_id=p.d_id,
                                   day=p.day,
                                   point=p.point)

    if updated_area is None or updated_area == 1:
        raise HTTPException(status_code=404,detail=f'{p.day},{p.point} not found')

    if updated_area == 0 :
        raise HTTPException(status_code=404,detail=f'd_id not found')

    return {
        'status':'Success, Driver_id&Driver_name',
        'Updated distribution point':updated_area
    }

# request format: http://127.0.0.1:{{port}}/areas/del?day=monday&point=1
@areas_router.delete('/day_point/del')
def delete_area(day:str,point:int):
    deleted = delete_day_area(day,point)
    if not deleted:
        raise HTTPException(status_code=404,detail=f'{day},{point} not found')
    return {
        'status':'Success',
        'Deleted distribution point':f'{day},{point} point Deleted'
    }

