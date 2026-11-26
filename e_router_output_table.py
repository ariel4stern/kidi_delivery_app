import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel,Field
from typing import Optional


from e_dal_output_table import (
    get_all_rows_output,
    get_row_output,
    insert_row_output,
    update_output_point_driver_id,
    patch_output_row,
    delete_row_output,
    delete_output_table,
    initialize_output_table
)

output_router = APIRouter(
    prefix="/output_data",
    tags=["output_data"]
)

BASE_DIR = os.getcwd()
REPORTS_DIR_PATH = os.path.join(BASE_DIR,"distribution_reports")

class OutputData(BaseModel):
    output_number : float = Field(...,gt=0)
    output_count : int = Field(...,gt=0)
    driver_id : Optional[int] = Field(None,gt=0)
    note : Optional[str] = Field(None,min_length=2)

class PatchOutputData(BaseModel):
    output_count : Optional[int] = not Field(None,gt=0)
    driver_id : Optional[int] = Field(None,gt=0)
    note : Optional[str] = Field(None,min_length=2)


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
                                 driver_id=output_data.driver_id,
                                 note=output_data.note)
    if inserted is None:
        raise HTTPException(status_code=404, detail="output row Failed to insert.")

    return {
        'status':"Success",
        'inserted_row': inserted
    }


@output_router.put("/{output_number}")
def update_output_data_by_number(output_number:float,output_driver_id:int):
    updated_row = get_row_output(output_number)
    if updated_row is None:
        raise HTTPException(status_code=404, detail="No output row found.")
    updated_driver = update_output_data_by_number(output_number,output_driver_id)
    if updated_driver is None:
        raise HTTPException(status_code=404, detail="Output driver failed to update.")
    return {
        'status':"Success",
        'updated_row': updated_row
    }

@output_router.patch("/patch/{output_number}")
def patch_output_data(output_number,output_data:PatchOutputData):
    patched_row = patch_output_row(store_number=output_number,
                                   store_count=output_data.output_count,
                                   driver_id=output_data.driver_id,
                                   note=output_data.note)

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
d = PatchOutputData(output_count=4, driver_id=1 ,note='hello')
patched = patch_output_row(store_number=3,
                                   store_count=d.output_count,
                                   driver_id=d.driver_id,
                                   note=d.note)
print(patched)
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
def refresh_output_table_data():
    deleted_table = delete_output_table()
    if not deleted_table:
        raise HTTPException(status_code=404, detail="No output row found.")

    if not initialize_output_table():
        raise HTTPException(status_code=404, detail="Output table failed to initialize.")

    return {
        'status':"Success",
        'details': "Table output_data deleted successfully."
    }



