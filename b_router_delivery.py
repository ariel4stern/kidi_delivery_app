from fastapi import APIRouter,HTTPException
from typing import List
from pydantic import BaseModel,Field
from b_dal_delivery import (
    initialize_delivery_table,
    update_distribution_line,
    get_distribution_line,
    get_distribution_lines_table,
    clear_distribution_line,
    drop_distribution_line_table
)

delivery_router = APIRouter(
    prefix='/delivery',
    tags=['delivery'],
)

class UpdateDistributionLine(BaseModel):
    day: str = Field(...,min_length=1,max_length=10)
    distribution_line: List[int] = Field(...,min_length=1)

@delivery_router.get('/')
def get_all_distribution_line():
    dist_table = get_distribution_lines_table()
    if not dist_table:
        raise HTTPException(status_code=404,detail='Distribution lines Table not found.')
    return {'status': 'Success',
            'distribution lines': dist_table}

@delivery_router.get('/{day}')
def get_delivery(day:str):
    dist_line = get_distribution_line(day)
    if dist_line is None:
        raise HTTPException(status_code=404,detail='Distribution line not found.')
    return {'status': 'Success',
            'distribution line': dist_line}

@delivery_router.put('/up')
def update_existing_distribution_line(updating_distribution_line:UpdateDistributionLine):
    updated_distribution_line = update_distribution_line(day=updating_distribution_line.day,
                                                         distribution_line_l=updating_distribution_line.distribution_line)
    if updated_distribution_line is None:
        raise HTTPException(status_code=409,detail='day Not Found.')

    return {'status': 'Success',
            'distribution line updated': updated_distribution_line}

@delivery_router.delete('/del/{day}')
def clear_existing_distribution_line(day:str):
    done = clear_distribution_line(day)
    if not done:
        raise HTTPException(status_code=409,detail='day not found.')
    return {'status': 'Success',
            'cleared distribution line': get_distribution_line(day)}

@delivery_router.delete('/reset')
def reset_distribution_line():
    done = drop_distribution_line_table()
    if not done:
        raise HTTPException(status_code=409,detail='Distribution line Table Failed to Delete.')
    initialize_delivery_table()
    return {'status': 'Success',
            'detail': 'Distribution line Reset Successful'}

