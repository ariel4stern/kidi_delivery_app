from fastapi import APIRouter,HTTPException
from typing import List
from pydantic import BaseModel,Field
from b_dal_delivery import (
    initialize_delivery_table,
    patch_distribution_line,
    get_distribution_line,
    get_distribution_lines_table,
    clear_distribution_line,
    drop_distribution_line_table
)

delivery_router = APIRouter(
    prefix='/delivery',
    tags=['delivery'],
)

class PatchDistributionLine(BaseModel):
    day: str = Field(...,min_length=1,max_length=10)
    distribution_lines: List[int] = Field([],min_length=1)
    distribution_areas: List[str] = Field([],min_length=1)

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

@delivery_router.patch('/patch')
def patch_existing_distribution_line(updating_distribution_line:PatchDistributionLine):
    existing_distribution_line = get_distribution_line(updating_distribution_line.day)
    if existing_distribution_line is None:
        raise HTTPException(status_code=404,detail='day not found.')

    patched_distribution_line = patch_distribution_line(day=updating_distribution_line.day,
                                                         distribution_line_l=updating_distribution_line.distribution_lines,
                                                        distribution_area_l=updating_distribution_line.distribution_areas)
    if patched_distribution_line == 0:
        raise HTTPException(status_code=400,detail='No parameters provided as should.')

    if patched_distribution_line == 1:
        raise HTTPException(status_code=404,detail='Distribution line not found.')

    if patched_distribution_line == 2:
        raise HTTPException(status_code=409,detail='Failed to find distribution line.')

    return {'status': 'Success',
            'distribution line updated': patched_distribution_line}

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

