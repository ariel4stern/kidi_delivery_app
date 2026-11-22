from fastapi import APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel,Field
from d_dal_points import (
    get_all_dist_point,
    get_dist_point,
    insert_new_day_point,
    update_day_point,
    delete_day_point
)
point_router = APIRouter(
    tags=['points'],
    prefix='/points',
)

class Point(BaseModel):
    d_id : Optional[int] = Field(None,gt=0,lt=10)
    day : str = Field(...,min_length=2,max_length=20)
    point : int = Field(0,gt=0)

class UpdatePoint(BaseModel):
    d_id : int = Field(...,gt=0,lt=10)
    day : str = Field(...,min_length=2,max_length=20)
    point : int = Field(...,gt=0)

@point_router.get('/')
def get_points():
    d_point = get_all_dist_point()
    if d_point is None:
        raise HTTPException(status_code=404,detail='Table point_distributions not found')
    return {
        'status':'Success',
        'distribution_points':d_point
    }

# request format: http://127.0.0.1:{{port}}/points/day_point?day=sunday&point=1
@point_router.get('/day_point')
def get_point_distributions(day:str,point:int):
    selected_point = get_dist_point(day,point)
    if selected_point is None:
        raise HTTPException(status_code=404,detail=f'{day,point} not found')
    return {
        'status':'Success',
        'distribution_point':selected_point
    }

@point_router.post('/day_point/in')
def insert_point(p:Point):
    inserted_dict = insert_new_day_point(d_id=p.d_id,
                                        day=p.day,
                                        point=p.point)

    if inserted_dict == 0:
        raise HTTPException(status_code=404,detail='Driver_id not found')

    if inserted_dict == 1:
        raise HTTPException(status_code=404,detail=f'inserting point: ({p.day},{p.point}) --problem in db')

    if inserted_dict == 2:
        raise HTTPException(status_code=404,detail=f'problem inserting point ({p.day},{p.point}) --unique constraint')

    return {
        'status':'Success',
        'New distribution point':inserted_dict
    }

@point_router.put('/day_point/up')
def update_area(p:UpdatePoint):
    updated_point = update_day_point(d_id=p.d_id,
                                   day=p.day,
                                   point=p.point)

    if updated_point is None or updated_point == 1:
        raise HTTPException(status_code=404,detail=f'{p.day},{p.point} not found')

    if updated_point == 0 :
        raise HTTPException(status_code=404,detail=f'd_id not found')

    return {
        'status':'Success, Driver_id & Driver_name',
        'Updated distribution point':updated_point
    }

# request format: http://127.0.0.1:{{port}}/points/del?day=monday&point=1
@point_router.delete('/day_point/del')
def delete_point(day:str,point:int):
    deleted = delete_day_point(day,point)
    if not deleted:
        raise HTTPException(status_code=404,detail=f'{day},{point} not found')
    return {
        'status':'Success',
        'Deleted distribution point':f'{day},{point} point Deleted'
    }

