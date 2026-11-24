"""main_page.py - runs the delivery_distribution website.

Local :  python main_page.py            (or: uvicorn main_page:app --reload)
Public:  set APP_USER + APP_PASSWORD (strongly recommended), then
         python main_page.py            (or: uvicorn main_page:app --host 0.0.0.0 --port $PORT)

Environment variables (all optional):
  HOST          bind address              (default 0.0.0.0)
  PORT          port                      (default 8000)
  RELOAD        1 = auto reload (dev)     (default off)
  APP_USER      basic-auth user           (default "admin")
  APP_PASSWORD  basic-auth password       (if empty -> NO login, local use only!)
  DATA_DIR      folder for the .db file and distribution_reports/ (default: this folder)
"""
import base64
import os
import secrets
import sqlite3
import sys
from pathlib import Path
from typing import List

BASE = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("DATA_DIR", BASE)).resolve()
DATA_DIR.mkdir(parents=True, exist_ok=True)
if str(BASE) not in sys.path:          # modules are imported by name, keep them findable after chdir
    sys.path.insert(0, str(BASE))
os.chdir(DATA_DIR)                     # the DAL files use a relative DB name; f_functions uses os.getcwd()

import pandas as pd
from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from a_dal_stores import initialize_stores
from b_dal_delivery import initialize_delivery_table
from c_dal_drivers import (initialize_drivers, get_drivers_name_ids_status, get_drivers_name_ids,
                           update_driver_available_not, reset_cartoons_count)
from d_dal_points import (initialize_point_distributions, get_all_dist_point,
                          update_day_point as dal_update_day_point)
from e_dal_output_table import (initialize_output_table, get_all_rows_output, get_row_output,
                                update_output_count_driver_null, get_connection, get_current_day)
from eb_dal_output_table_two import create_output_table_two

import a_router_store as r_store
import b_router_delivery as r_deliv
import c_router_drivers as r_drv
import d_router_points as r_pts
import e_router_output_table as r_out
import eb_router_output_table_two as r_out2
from f_functions import (counting_confirmation, convert_output_table_to_df,
                         allocation_division_distribution_points, merged_output_tables, export_excel,
                         insert_to_output_two_all_null)
from dotenv import load_dotenv

BASE = Path(__file__).resolve().parent
load_dotenv(BASE / ".env")          # real environment variables still win over the file

DATA_DIR = Path(os.environ.get("DATA_DIR", BASE)).resolve()

APP_USER = os.environ.get("APP_USER", "admin")
APP_PASSWORD = os.environ.get("APP_PASSWORD", "kidi8080")

app = FastAPI(title="delivery_distribution")
app.add_middleware(GZipMiddleware, minimum_size=1000)

# ---- database bootstrap (order matters: drivers before point_distributions) ----
initialize_stores()
initialize_delivery_table()
initialize_drivers()
initialize_point_distributions()
initialize_output_table()
create_output_table_two()   # f_functions / export_excel expect this table to exist

for r in (r_store.stores_router, r_deliv.delivery_router, r_drv.drivers_router,
          r_pts.point_router, r_out.output_router, r_out2.output_two_router):
    app.include_router(r)
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")


# ---------------------------------------------------------------- public server: login + health
@app.middleware("http")
async def basic_auth(request: Request, call_next):
    """HTTP basic auth for the whole site (pages, API and the routers) when APP_PASSWORD is set."""
    if not APP_PASSWORD or request.url.path == "/healthz":
        return await call_next(request)
    header = request.headers.get("authorization", "")
    ok = False
    if header.lower().startswith("basic "):
        try:
            user, _, pwd = base64.b64decode(header[6:]).decode("utf-8").partition(":")
            ok = (secrets.compare_digest(user.encode(), APP_USER.encode()) and
                  secrets.compare_digest(pwd.encode(), APP_PASSWORD.encode()))
        except Exception:
            ok = False
    if ok:
        return await call_next(request)
    return Response("Login required", status_code=401,
                    headers={"WWW-Authenticate": 'Basic realm="delivery_distribution", charset="UTF-8"'})


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


# ---------------------------------------------------------------- pages
def _tpl(name: str) -> str:
    return (BASE / "templates" / name).read_text(encoding="utf-8")


SHELL = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#ffa94d"><title>Delivery Distribution</title>
<link rel="stylesheet" href="/static/style.css"><script src="/static/common.js"></script></head>
<body><div id="sky"></div>
<nav class="tabs"><a href="/" class="home">&#8962; Welcome</a><a href="#tab1">Cartoons Counting</a>
<a href="#tab2">Save as Excel</a><a href="#tab3">Updating DataBase</a></nav>
<main>__TABS__</main></body></html>"""


@app.get("/", response_class=HTMLResponse)
def welcome():
    return _tpl("welcome.html")


@app.get("/app", response_class=HTMLResponse)
def landing():
    tabs = "".join(_tpl(n) for n in ("tab1_counting.html", "tab2_save_print.html", "tab3_database.html"))
    return SHELL.replace("__TABS__", tabs)


def _records(df: pd.DataFrame):
    """DataFrame -> list of dicts with NaN replaced by None (valid JSON)."""
    return df.astype(object).where(pd.notna(df), None).to_dict("records")


# ---------------------------------------------------------------- tab 1 api (counting)
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
        raise HTTPException(404, f"Store number {row.store_number} not found in the output table.")
    return {"row": done}


@app.post("/api/counting/finish")
def api_count_finish(batch: CountBatch):
    if not batch.rows:
        raise HTTPException(400, "No rows were sent. Reload the page and count again.")

    missing = [r.store_number for r in batch.rows if get_row_output(r.store_number) is None]
    if missing:
        raise HTTPException(400, f"Store number(s) {missing} not found in the output table. "
                                 "Reload the page and count again.")

    # counting_confirmation(dataframe): store_numbers | cartoons_count (cartoons + bags) | driver_id (None)
    df = pd.DataFrame({"store_numbers": [r.store_number for r in batch.rows],
                       "cartoons_count": [r.cartoons + r.bags for r in batch.rows],
                       "driver_id": [None] * len(batch.rows)})
    if not counting_confirmation(df):
        raise HTTPException(400, "The counts could not be saved: a store number was not found in the output table.")

    # allocation works on rows whose driver is NULL ("not allocated yet"). Safety net for databases that
    # were created with the old default (driver_id = 5 'nobody').
    with get_connection() as conn:
        conn.execute("UPDATE output_data SET driver_id = NULL, driver_name = NULL")

    full = convert_output_table_to_df()
    if full is None:
        raise HTTPException(409, "The output table is empty.")
    full = full.rename(columns={"store_number": "store_numbers", "store_count": "cartoons_count"})

    try:
        result = allocation_division_distribution_points(full)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Allocation failed: {type(e).__name__}: {e}")
    if result is None:
        raise HTTPException(409, "Allocation did not run. Check that every store has a distribution point today.")

    # every store that still has no driver (NaN) goes to output_data_two
    try:
        moved = insert_to_output_two_all_null() or 0
    except Exception as e:
        raise HTTPException(500, f"Saving the unallocated stores to output_data_two failed: {type(e).__name__}: {e}")
    return {"detail": "Success You allow to move on", "moved_to_output_two": moved}


# ---------------------------------------------------------------- tab 2 api (result + excel)
@app.get("/api/output")
def api_output():
    """Tab 2: output_data + output_data_two (merged_output_tables) - the same table that is exported to Excel."""
    try:
        df = merged_output_tables()
    except Exception as e:
        raise HTTPException(500, f"{type(e).__name__}: {e}")
    if df is None or df.empty:
        return {"rows": []}
    return {"rows": _records(df)}


@app.get("/api/export")
def api_export():
    try:
        path = export_excel()
    except Exception as e:
        raise HTTPException(500, f"Excel export failed: {type(e).__name__}: {e}")
    return FileResponse(path, filename=Path(path).name,
                        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


# ---------------------------------------------------------------- toolbar api
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


@app.post("/api/maintenance/reset_counts")
def api_reset_counts():
    """Toolbar option 1: reset_cartoons_count() - every driver's cartoons_count back to 0."""
    try:
        n = reset_cartoons_count()
    except sqlite3.Error as e:
        raise HTTPException(400, f"Database error: {e}")
    if not n:
        raise HTTPException(404, "No drivers found, nothing was reset.")
    return {"detail": f"Cartoons count was reset to 0 for {n} driver(s)."}


@app.post("/api/maintenance/refresh_output_two")
def api_refresh_output_two():
    """Toolbar option 2: refresh_output_table_data() from eb_router_output_table_two.py."""
    try:
        r_out2.refresh_output_table_data()
    except HTTPException as e:
        if e.status_code == 404:   # the router raises 404 when there was nothing to delete
            return {"detail": "output_data_two was already empty. Nothing to refresh."}
        raise
    except sqlite3.Error as e:
        raise HTTPException(400, f"Database error: {e}")
    return {"detail": "output_data_two was refreshed (all rows deleted)."}


# ---------------------------------------------------------------- tab 3 api (router functions)
@app.get("/api/merged")
def api_merged():
    """merged_output_tables() -> output_data + output_data_two (used by the unique button)."""
    try:
        df = merged_output_tables()
    except Exception as e:
        raise HTTPException(500, f"{type(e).__name__}: {e}")
    if df is None or df.empty:
        return {"rows": []}
    return {"rows": _records(df)}


def _no(x: dict, key: str = "output_number") -> int:
    if key not in x:
        raise HTTPException(400, f"'{key}' is required.")
    return int(x.pop(key))


def _patch_two(x: dict):
    """patch_output_two_data with output_count forced to null: only the driver of the row is changed."""
    number = _no(x)
    if x.get("driver_id") is None:
        raise HTTPException(400, "'driver_id' is required.")
    return r_out2.patch_output_two_data(number, r_out2.PatchOutputData(output_count=None,
                                                                       driver_id=x["driver_id"]))


R_STORE, R_DELIV, R_DRV, R_PTS = "a_router_store.py", "b_router_delivery.py", "c_router_drivers.py", "d_router_points.py"
R_OUT, R_OUT2 = "e_router_output_table.py", "eb_router_output_table_two.py"

REG = {  # router file -> function -> (JSON template, caller)
    R_STORE: {
        "insert_store": ({"store_number": 100, "store_name": "name", "store_area": "area"},
                         lambda x: r_store.insert_store(r_store.Store(**x))),
        "patch_store": ({"store_number": 1, "store_name": "new name", "store_area": "new area"},
                        lambda x: r_store.patch_store(_no(x, "store_number"), r_store.StoreUpdate(**x))),
        "delete_existing_store": ({"store_number": 100},
                                  lambda x: r_store.delete_existing_store(int(x["store_number"]))),
    },
    R_DELIV: {
        "patch_existing_distribution_line": (
            {"day": "sunday", "stores_numbers": [1, 3], "distribution_areas": ["area"]},
            lambda x: r_deliv.patch_existing_distribution_line(r_deliv.PatchDistributionLine(**x))),
    },
    R_DRV: {
        "insert_new_driver": ({"name": "name", "phone": "0500000000"},
                              lambda x: r_drv.insert_new_driver(r_drv.NewDriver(**x))),
        "patch_existing_driver": (
            {"driver_id": 1, "name": "name", "phone": "0500000000", "status": "available",
             "cartoons_count": 1, "max_cartoons": 200},
            lambda x: r_drv.patch_existing_driver(_no(x, "driver_id"), r_drv.PatchDriver(**x))),
        "delete_existing_driver": ({"driver_id": 1},
                                   lambda x: r_drv.delete_existing_driver(int(x["driver_id"]))),
    },
    R_PTS: {
        "insert_point": ({"d_id": 1, "day": "sunday", "point": 3},
                         lambda x: r_pts.insert_point(r_pts.Point(**x))),
        "update_day_point": ({"d_id": 1, "day": "sunday", "point": 3},
                             lambda x: r_pts.update_day_point(r_pts.UpdatePoint(**x))),
        "delete_point": ({"day": "sunday", "point": 3},
                         lambda x: r_pts.delete_point(str(x["day"]), int(x["point"]))),
    },
    R_OUT: {
        "get_output_data": ({}, lambda x: r_out.get_output_data()),
        "insert_new_output_row": ({"output_number": 3, "output_count": 10, "driver_id": 1},
                                  lambda x: r_out.insert_new_output_row(r_out.OutputData(**x))),
        "patch_output_data": ({"output_number": 3, "output_count": 10, "driver_id": 1},
                              lambda x: r_out.patch_output_data(_no(x), r_out.PatchOutputData(**x))),
        "delete_output_data_by_number": ({"output_number": 3},
                                         lambda x: r_out.delete_output_data_by_number(_no(x))),
        "refresh_output_table_data": ({}, lambda x: r_out.refresh_output_table_data()),
    },
    R_OUT2: {
        # "patch_output_two_data" has its own button in Tab 3 (hidden from the function list)
        # output_count is not asked from the user: it is always sent as null (None) from here
        "patch_output_two_data": ({"output_number": 3, "driver_id": 1}, lambda x: _patch_two(x)),
        "refresh_output_table_data": ({}, lambda x: r_out2.refresh_output_table_data()),
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


@app.post("/api/manage/{router}/{func}")
def manage_call(router: str, func: str, body: dict = Body(default={})):
    print(router)
    spec = REG.get(router, {}).get(func)
    if spec is None:
        raise HTTPException(404, "Unknown router/function.")
    return _run(spec[1], body)


if __name__ == "__main__":
    import uvicorn

    if not APP_PASSWORD:
        print("WARNING: APP_PASSWORD is not set - the site (including database editing) has NO login. "
              "Set APP_USER / APP_PASSWORD before exposing it publicly.")
    uvicorn.run("main_page:app",
                host=os.environ.get("HOST", "0.0.0.0"),
                port=int(os.environ.get("PORT", "8000")),
                reload=os.environ.get("RELOAD", "0") == "1",
                proxy_headers=True, forwarded_allow_ips="*")
