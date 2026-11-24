import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel,Field
from typing import Optional


from eb_dal_output_table_two import (
    create_output_table_two,
    get_all_rows_output_two,
    get_row_output_two,
    insert_row_output_two,
    patch_output_row_two,
    update_output_two_number,
    delete_output_table_two
)

output_two_router = APIRouter(
    prefix="/output_data_two",
    tags=["output_data_two"]
)

BASE_DIR = os.getcwd()
REPORTS_DIR_PATH = os.path.join(BASE_DIR,"distribution_reports")

class OutputDataTwo(BaseModel):
    output_number : float = Field(...,gt=0)
    output_count : int = Field(...,gt=0)
    driver_id : Optional[int] = Field(None,gt=0)

class PatchOutputDataTwo(BaseModel):
    output_count : Optional[int] = Field(None,gt=0)
    driver_id : Optional[int] = Field(None,gt=0)

class UpdateOutputDataId(BaseModel):
    output_driver_id : int = Field(...,gt=0)

@output_two_router.get("/")
def get_output_data_two():
    output_data = get_all_rows_output_two()
    if output_data is None:
        raise HTTPException(status_code=404, detail="No output data found.")
    return {
        'status':"Success",
        'data': output_data
    }

@output_two_router.get("/{output_number}")
def get_output_data_two_by_number(output_number:int):
    output_row = get_row_output_two(output_number)
    if output_row is None:
        raise HTTPException(status_code=404, detail="No output row found.")

    return {
        'status':"Success",
        'data': output_row
    }

@output_two_router.post("/in")
def insert_new_output_two_row(output_data:OutputDataTwo):
    inserted = insert_row_output_two(store_number=output_data.output_number,
                                 store_count=output_data.output_count,
                                 driver_id=output_data.driver_id)
    if inserted == 1:
        raise HTTPException(status_code=404, detail="driver_id not found.")
    if inserted == 2:
        raise HTTPException(status_code=404, detail="store_number failed to insert.")
    if inserted == 3:
        raise HTTPException(status_code=404, detail="Unique Constrain store_number failed to insert.")

    return {
        'status':"Success",
        'inserted_row': inserted
    }

@output_two_router.put("/up/{output_number}")
def update_output_data_two_by_number(output_number:float,up_driver_id:UpdateOutputDataId):
    updated_row = get_row_output_two(output_number)
    if updated_row is None:
        raise HTTPException(status_code=404, detail="No output row found.")
    updated_driver = update_output_two_number(output_number,up_driver_id.output_driver_id)
    if updated_driver == 0:
        raise HTTPException(status_code=404, detail="driver_id not found ,FOREIGN KEY constraint failed.")

    return {
        'status':"Success",
        'updated_row': get_row_output_two(output_number)
    }

@output_two_router.patch("/patch/{output_number}")
def patch_output_two_data(output_number:int,output_data:PatchOutputDataTwo):
    patched_row_two = patch_output_row_two(store_number=output_number,
                                   store_count=output_data.output_count,
                                   driver_id=output_data.driver_id)
    if patched_row_two == 0:
        raise HTTPException(status_code=404, detail="parameters provided Wrong.")

    if patched_row_two == 1:
        raise HTTPException(status_code=404, detail="Not such row in output table.")

    if patched_row_two == 2:
        raise HTTPException(status_code=404, detail="Row failed to patch.")

    return {
        'status':"Success",
        'updated_row': patched_row_two
    }

@output_two_router.delete("/delete/table")
def refresh_output_table_data_two():
    deleted_table = delete_output_table_two()
    if not deleted_table:
        raise HTTPException(status_code=404, detail="No output row found.")

    create_output_table_two()

    return {
        'status':"Success",
        'details': "Table output_data_two deleted successfully."
    }



