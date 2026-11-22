from fastapi import APIRouter, HTTPException
from pydantic import BaseModel,Field
from typing import Optional
from e_dal_output_table import (
    get_all_rows_output,
    get_row_output,
    insert_row_output,
    patch_output_row,
    delete_row_output,
    delete_output_table,
    get_current_day
)

output_router = APIRouter(
    prefix="/output_data",
    tags=["output_data"]
)

class OutputData(BaseModel):
    output_number : float = Field(...,gt=0)
    output_count : int = Field(...,gt=0)
    driver_id : Optional[int] = Field(None,gt=0)

class PatchOutputData(BaseModel):
    output_count : Optional[int] = not Field(None,gt=0)
    driver_id : Optional[int] = Field(None,gt=0)

@output_router.get("/")
def get_output_data():
    output_data = get_all_rows_output()
    if output_data is None:
        raise HTTPException(status_code=404, detail="No output data found.")
    return {
        'status':"Success",
        'data': output_data
    }

@output_router.get("/{output_number}")
def get_output_data_by_number(output_number:int):
    output_row = get_row_output(output_number)
    if output_row is None:
        raise HTTPException(status_code=404, detail="No output row found.")

    return {
        'status':"Success",
        'data': output_row
    }

@output_router.post("/in")
def insert_new_output_row(output_data:OutputData):
    inserted = insert_row_output(store_number=output_data.output_number,
                                 store_count=output_data.output_count,
                                 driver_id=output_data.driver_id)
    if inserted is None:
        raise HTTPException(status_code=404, detail="output row Failed to insert.")

    return {
        'status':"Success",
        'inserted_row': inserted
    }

@output_router.patch("/patch/{output_number}")
def patch_output_data(output_number,output_data:PatchOutputData):
    patched_row = patch_output_row(store_number=output_number,
                                   store_count=output_data.output_count,
                                   driver_id=output_data.driver_id)
    if patched_row == 0:
        raise HTTPException(status_code=404, detail="parameters provided Wrong.")

    if patched_row == 1:
        raise HTTPException(status_code=404, detail="Not such row in output table.")

    if patched_row == 2:
        raise HTTPException(status_code=404, detail="Row failed to patch.")

    return {
        'status':"Success",
        'updated_row': patched_row
    }

@output_router.delete("/del/{output_number}")
def delete_output_data_by_number(output_number:int):
    deleted = get_output_data_by_number(output_number)
    if deleted is None:
        raise HTTPException(status_code=404, detail="No output row found.")

    deleted_done = delete_row_output(output_number)
    if not deleted_done:
        raise HTTPException(status_code=404, detail="Failed to Delete row.")

    return {
        'status':"Success",
        'deleted row': deleted
    }

@output_router.delete("/delete/table")
def delete_output_data_by_number():
    deleted_table = delete_output_table()
    if not deleted_table:
        raise HTTPException(status_code=404, detail="No output row found.")

    return {
        'status':"Success",
        'details': "Table output_data deleted successfully."
    }



