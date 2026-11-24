import sqlite3
from contextlib import contextmanager
from typing import Iterator, List, Any, Dict
from datetime import datetime

from select import select

from b_dal_delivery import (
    get_today_store_numbers
)

DB_NAME = 'deliveries_distribution.db'

@contextmanager
def get_connection() -> Iterator[sqlite3.Connection] :
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")

    try:
        yield conn
        conn.commit()

    except sqlite3.OperationalError:
        conn.rollback()
        raise

    finally:
        conn.close()
def rows_exists(table_name:str) -> bool :
    query = f'''SELECT EXISTS(SELECT 1 FROM {table_name});'''
    with get_connection() as conn:
        cursor = conn.execute(query).fetchone()
        return bool(cursor[0])
def get_current_day():
    today = datetime.now()

    day_name = today.strftime("%A")

    return day_name.lower()

def create_output_table() -> None :
    query = '''
    CREATE TABLE IF NOT EXISTS output_data (
        store_number REAL PRIMARY KEY,
        store_count INTEGER DEFAULT 0,
        driver_id INTEGER DEFAULT null,
        driver_name TEXT DEFAULT null,
        
        FOREIGN KEY (driver_id)
        REFERENCES drivers (driver_id)
        ON DELETE SET NULL
        );'''
    with get_connection() as conn:
        conn.execute(query)
def insert_auto_fields() -> int :
    today = get_current_day()
    today_numbers = get_today_store_numbers(today)
    if today_numbers is None:
        return 404

    query = '''
    INSERT INTO output_data (store_number)
    VALUES (?)'''
    with get_connection() as conn:
        cursor = conn.executemany(query, [(num,) for num in today_numbers])
        return cursor.rowcount
def initialize_output_table()-> bool | None :
    create_output_table()
    if rows_exists("output_data"):
        print(f'output_data Table already exists.')
        return False

    inserted = insert_auto_fields()
    print(f'output_data Table initialized successfully. {inserted} new row added.')
    return True

def get_row_output(store_number:float) -> Dict[str,Any] | None :
    query = '''
    SELECT store_number, store_count, driver_id, driver_name FROM output_data WHERE store_number = ?'''
    with get_connection() as conn:
        row = conn.execute(query, (store_number,)).fetchone()
        if row is None:
            return None
        return dict(row)
def get_all_rows_output() -> List[Dict[str,Any]] | None :
    query = '''
    SELECT store_number, store_count, driver_id, driver_name FROM output_data
    '''
    try:
        with get_connection() as conn:
            rows = conn.execute(query).fetchall()
            if not rows:
                return []
            return [dict(row) for row in rows]
    except sqlite3.OperationalError as e:
        if 'not such table' in str(e):
            return None
        raise

def insert_row_output(store_number:float, store_count:int, driver_id) -> Dict[str,Any] | None :
    query = '''
    INSERT INTO output_data (store_number, store_count, driver_id)
    VALUES (?, ?, ?)
    '''
    parameters = [store_number, store_count, driver_id]
    if driver_id is not None:
        select_query = '''
        SELECT driver_name FROM drivers WHERE driver_id = ?'''
        with get_connection() as conn:
            cursor = conn.execute(select_query, (driver_id,)).fetchone()
            if cursor is None:
                raise ValueError(f"Not such driver_id {driver_id} ")
            driver_name = str(cursor[0])
            parameters.append(driver_name)

    with get_connection() as conn:
        cursor = conn.execute(query, (store_number, store_count, driver_id))
        if cursor.rowcount == 0:
            return None
    return get_row_output(store_number)

def patch_output_row(store_number,store_count,driver_id) -> int | Dict[str,Any] | None:
    if all(x is None for x in [store_number,store_count,driver_id]):
        print('store_number must be provided and with him driver_id')
        return 0

    existing_row = get_row_output(store_number)
    if existing_row is None:
        print('Not such row in output table')
        return 1

    query = '''
    UPDATE output_data SET'''
    parameters = []


    if store_count is not None:
        query = query + ' store_count = ?,'
        parameters.append(store_count)

    if driver_id is not None:
        query = query + ' driver_id = ?,'
        parameters.append(driver_id)
        select_query = '''
                SELECT driver_name FROM drivers WHERE driver_id = ?
            '''
        with get_connection() as conn:
            cursor = conn.execute(select_query, (driver_id,)).fetchone()
            if cursor is None:
                raise ValueError(f"Not such driver_id {driver_id} ")
            driver_name = str(cursor[0])
            query = query + ' driver_name = ?,'
            parameters.append(driver_name)


    query = query.rstrip(', ') + ' WHERE store_number = ?'
    parameters.append(int(store_number))

    with get_connection() as conn:
        cursor = conn.execute(query, parameters)
        if cursor.rowcount == 0:
            return 2

    return get_row_output(store_number)
def update_output_number(st_number:float,count:int,d_id:int) -> Dict[str,Any] | None:
    query = '''
    UPDATE output_data SET
        store_number = ?,
        store_count  = ?,
        driver_id = ?,
        driver_name  = (SELECT driver_name FROM drivers WHERE driver_id = ?)
    WHERE store_number = ?
    '''
    with get_connection() as conn:
        cursor = conn.execute(query, (st_number,count,d_id,d_id,st_number))
        if cursor.rowcount == 0:
            return None

    return get_row_output(st_number)
def update_output_count_driver_null(st_number:float,count:int) -> Dict[str,Any] | None:
    query = '''
    UPDATE output_data SET
        store_count  = ?
    WHERE store_number = ?
    '''
    with get_connection() as conn:
        cursor = conn.execute(query, (count,st_number))
        if cursor.rowcount == 0:
            return None

    return get_row_output(st_number)
def update_output_point_driver_id(st_number:float,driver_id:int) -> Dict[str,Any] | None:
    query = '''
    UPDATE output_data SET 
            driver_id = ?
            WHERE store_number = ?'''
    with get_connection() as conn:
        cursor = conn.execute(query, (driver_id,st_number))
        if cursor.rowcount == 0:
            return None
    return get_row_output(st_number)
def clear_output_driver(st_number:float, count:int) -> Dict[str,Any] | None:
    query = '''
    UPDATE output_data SET store_count = ?, driver_id = NULL, driver_name = NULL
    WHERE store_number = ?'''
    with get_connection() as conn:
        cursor = conn.execute(query, (count, st_number))
        if cursor.rowcount == 0:
            return None
    return get_row_output(st_number)

def delete_row_output(store_number:float) -> bool :
    query = '''
    DELETE FROM output_data WHERE store_number = ?'''
    with get_connection() as conn:
        cursor = conn.execute(query, (store_number,))
        return cursor.rowcount > 0

def delete_output_table()-> bool :
    query = '''
    DELETE FROM output_data;'''
    with get_connection() as conn:
        cursor = conn.execute(query)
        return cursor.rowcount > 0
def refresh_output_table() -> bool:
    query = '''
    UPDATE output_data SET
        store_count = 0,
        driver_id = NULL,
        driver_name = NULL;
    '''
    with get_connection() as conn:
        cursor = conn.execute(query)
        return cursor.rowcount > 0






