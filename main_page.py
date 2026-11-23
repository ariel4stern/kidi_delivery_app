"""main_page.py - runs the delivery_distribution website (uvicorn main_page:app --reload)."""
import sqlite3
from pathlib import Path
from typing import List

import pandas as pd
from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from a_dal_stores import initialize_stores
from c_dal_drivers import get_drivers_name_ids_status, get_drivers_name_ids, update_driver_available_not
from d_dal_points import get_all_dist_point, update_day_point as dal_update_day_point
from b_dal_delivery import initialize_delivery_table
from c_dal_drivers import initialize_drivers
from d_dal_points import initialize_point_distributions
from e_dal_output_table import initialize_output_table, get_all_rows_output, get_row_output, \
    update_output_count_driver_null, get_connection, get_current_day

import a_router_store as r_store
import b_router_delivery as r_deliv
import c_router_drivers as r_drv
import d_router_points as r_pts
import e_router_output_table as r_out
from f_functions import counting_confirmation, convert_output_table_to_df, \
    allocation_division_distribution_points, export_excel, print_last_report

BASE = Path(__file__).parent
app = FastAPI(title="delivery_distribution")

initialize_stores(); initialize_delivery_table(); initialize_drivers()
initialize_point_distributions(); initialize_output_table()

for r in (r_store.stores_router, r_deliv.delivery_router, r_drv.drivers_router,
          r_pts.point_router, r_out.output_router):
    app.include_router(r)
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")

# ---------------------------------------------------------------- pages
def _tpl(name: str) -> str:
    return (BASE / "templates" / name).read_text(encoding="utf-8")

SHELL = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Delivery Distribution</title>
<link rel="stylesheet" href="/static/style.css"><script src="/static/common.js"></script></head>
<body><div id="sky"></div>
<nav class="tabs"><a href="/" class="home">&#8962; Welcome</a><a href="#tab1">Cartoons Counting</a>
<a href="#tab2">Save and Print</a><a href="#tab3">Updating DataBase</a></nav>
<main>__TABS__</main></body></html>"""

@app.get("/", response_class=HTMLResponse)
def welcome():
    return _tpl("welcome.html")

@app.get("/app", response_class=HTMLResponse)
def landing():
    tabs = "".join(_tpl(n) for n in ("tab1_counting.html", "tab2_save_print.html", "tab3_database.html"))
    return SHELL.replace("__TABS__", tabs)

# ---------------------------------------------------------------- tab 1 / 2 api
class CountRow(BaseModel):
    store_number: int
    cartoons: int = Field(..., ge=0)
    bags: int = Field(..., ge=0)

class CountBatch(BaseModel):
    rows: List[CountRow]

@app.get("/api/rows")
def api_rows():
    return {"rows": get_all_rows_output() or []}

@app.post("/api/counting/row")
def api_count_row(row: CountRow):
    done = update_output_count_driver_null(st_number=row.store_number, count=row.cartoons + row.bags)
    if done is None:
        raise HTTPException(404, f"Store number {row.store_number} not found in output table.")
    return {"row": done}

@app.post("/api/counting/finish")
def api_count_finish(batch: CountBatch):
    df = pd.DataFrame({"store_numbers": [r.store_number for r in batch.rows],
                       "cartoons_count": [r.cartoons + r.bags for r in batch.rows],
                       "driver_id": [None] * len(batch.rows)})
    if not counting_confirmation(df):
        raise HTTPException(400, "A store number was not found in the output table. Reload the page and count again.")
    # output_data defaults driver_id to 5 ('nobody'); allocation expects NULL = "not allocated yet".
    with get_connection() as conn:
        conn.execute("UPDATE output_data SET driver_id = NULL, driver_name = NULL")
    full = convert_output_table_to_df()
    if full is None:
        raise HTTPException(409, "Output table is empty.")
    full = full.rename(columns={"store_number": "store_numbers", "store_count": "cartoons_count"})
    result = allocation_division_distribution_points(full)
    if result is None:
        raise HTTPException(409, "Allocation did not run. Check that drivers are 'available' "
                                 "and that every store has a distribution point today.")
    return {"detail": "Success You allow to move on"}

@app.get("/api/output")
def api_output():
    df = convert_output_table_to_df()
    if df is None:
        return {"rows": []}
    return {"rows": df.astype(object).where(pd.notna(df), None).to_dict("records")}

@app.get("/api/export")
def api_export():
    path = export_excel()
    return FileResponse(path, filename=Path(path).name,
                        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@app.post("/api/print")
def api_print():
    try:
        if not print_last_report():
            raise HTTPException(404, "No reports found. Download a report first.")
    except HTTPException:
        raise
    except Exception as e:  # os.startfile exists on Windows only
        raise HTTPException(500, f"Printing failed: {e}")
    return {"detail": "Print job sent."}

# ---------------------------------------------------------------- toolbar api (drivers availability / change point driver)
class AvailableBatch(BaseModel):
    driver_ids: List[int] = Field(..., min_length=1)

class ChangePointDriver(BaseModel):
    point: int = Field(..., gt=0)
    driver_id: int = Field(..., gt=0)

@app.get("/api/drivers/status")
def api_drivers_status():
    return {"drivers": get_drivers_name_ids_status()}

@app.get("/api/drivers/names")
def api_drivers_names():
    return {"drivers": get_drivers_name_ids()}

@app.post("/api/drivers/set_available")
def api_set_available(body: AvailableBatch):
    done, failed = [], []
    for d_id in dict.fromkeys(body.driver_ids):
        (done if update_driver_available_not(d_id, "available") else failed).append(d_id)
    if not done:
        raise HTTPException(404, f"No driver was updated. Unknown driver ids: {failed}")
    detail = f"Drivers set to 'available': {done}."
    if failed:
        detail += f" Not found: {failed}."
    return {"detail": detail, "updated": done, "failed": failed}

@app.get("/api/points/today")
def api_points_today():
    today = get_current_day()
    return {"day": today, "points": [r for r in (get_all_dist_point() or []) if r["day"] == today]}

@app.post("/api/points/change_driver")
def api_change_point_driver(body: ChangePointDriver):
    today = get_current_day()
    try:
        res = dal_update_day_point(body.driver_id, today, body.point)
    except sqlite3.Error as e:
        raise HTTPException(400, f"Database error: {e}")
    if not res:
        raise HTTPException(404, f"Point {body.point} not found for {today}.")
    return {"detail": f"Point {body.point} ({today}) now belongs to {res['driver_name']} (id {res['driver_id']}).",
            "point": res}

# ---------------------------------------------------------------- tab 3 api
OUT = "e_router_output_table.py"
REG = {  # router file -> function -> (JSON template, caller)
    "a_router_store.py": {
        "insert_store": ({"store_number": 100, "store_name": "name", "store_area": "area"},
                         lambda x: r_store.insert_store(r_store.Store(**x))),
        "patch_store": ({"store_number": 1, "store_name": "new name", "store_area": "new area"},
                        lambda x: r_store.patch_store(x.pop("store_number"), r_store.StoreUpdate(**x))),
        "delete_existing_store": ({"store_number": 100},
                                  lambda x: r_store.delete_existing_store(**x)),
    },
    "b_router_delivery.py": {
        "patch_existing_distribution_line": (
            {"day": "sunday", "stores_numbers": [1, 3], "distribution_areas": ["area"]},
            lambda x: r_deliv.patch_existing_distribution_line(r_deliv.PatchDistributionLine(**x))),
    },
    "c_router_drivers.py": {
        "insert_new_driver": ({"name": "name", "phone": "0500000000"},
                              lambda x: r_drv.insert_new_driver(r_drv.NewDriver(**x))),
        "patch_existing_driver": (
            {"driver_id": 1, "name": "name", "phone": "0500000000", "status": "available",
             "cartoons_count": 1, "max_cartoons": 200},
            lambda x: r_drv.patch_existing_driver(x.pop("driver_id"), r_drv.PatchDriver(**x))),
        "delete_existing_driver": ({"driver_id": 1}, lambda x: r_drv.delete_existing_driver(**x)),
    },
    "d_router_points.py": {
        "insert_point": ({"d_id": 1, "day": "sunday", "point": 3},
                         lambda x: r_pts.insert_point(r_pts.Point(**x))),
        "update_day_point": ({"d_id": 1, "day": "sunday", "point": 3},
                             lambda x: r_pts.update_day_point(r_pts.UpdatePoint(**x))),
        "delete_point": ({"day": "sunday", "point": 3}, lambda x: r_pts.delete_point(**x)),
    },
    OUT: {
        "get_output_data": ({}, lambda x: r_out.get_output_data()),
        "insert_new_output_row": ({"output_number": 3, "output_count": 10, "driver_id": 1},
                                  lambda x: r_out.insert_new_output_row(r_out.OutputData(**x))),
        "patch_output_data": ({"output_number": 3, "output_count": 10, "driver_id": 1},
                              lambda x: r_out.patch_output_data(
                                  int(x.pop("output_number")), r_out.PatchOutputData(**x))),
        "delete_output_data_by_number": ({"output_number": 3},
                                         lambda x: r_out.delete_output_data_by_number(int(x["output_number"]))),
        "refresh_output_table_data": ({}, lambda x: r_out.refresh_output_table_data()),
    },
}

def _run(fn, body):
    try:
        return {"ok": True, "result": fn(dict(body))}
    except HTTPException as e:
        return JSONResponse({"ok": False, "detail": e.detail}, status_code=e.status_code)
    except Exception as e:  # validation, bad JSON keys, sqlite, ...
        return JSONResponse({"ok": False, "detail": f"{type(e).__name__}: {e}"}, status_code=400)

@app.get("/api/manage/registry")
def manage_registry():
    return {k: {f: spec[0] for f, spec in v.items()} for k, v in REG.items()}

@app.post("/api/manage/patch_output")
def manage_patch_output(body: dict = Body(...)):
    def go(x):
        n = int(x["output_number"])
        return {"patched": REG[OUT]["patch_output_data"][1](x), "row": get_row_output(n)}
    return _run(go, body)

@app.post("/api/manage/{router}/{func}")
def manage_call(router: str, func: str, body: dict = Body(default={})):
    spec = REG.get(router, {}).get(func)
    if spec is None:
        raise HTTPException(404, "Unknown router/function.")
    return _run(spec[1], body)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_page:app", host="127.0.0.1", port=8000, reload=True)
