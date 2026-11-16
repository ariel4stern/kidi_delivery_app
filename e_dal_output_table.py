import sqlite3
from contextlib import contextmanager
from typing import Iterator, List, Any, Dict
from datetime import datetime
from b_dal_delivery import (
    get_today_store_numbers
)

DB_NAME = 'deliveries_distribution.db'

@contextmanager
def get_connection() -> Iterator[sqlite3.Connection] :
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row

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
        store_number INTEGER PRIMARY KEY,
        store_count INTEGER DEFAULT 0,
        driver_id INTEGER DEFAULT NULL,
        driver_name TEXT DEFAULT NULL,
    )'''
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

def get_row_output(store_number:int) -> Dict[str,Any] | None :
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

def insert_row_output(store_number:int, store_count:int, driver_id:int, driver_name:str) -> Dict[str,Any] | None :
    query = '''
    INSERT INTO output_data (store_number, store_count, driver_id, driver_name)
    VALUES (?, ?, ?, ?)
    '''
    with get_connection() as conn:
        cursor = conn.execute(query, (store_number, store_count, driver_id, driver_name))
        if cursor.rowcount == 0:
            return None
    return get_row_output(store_number)

def patch_output_row(store_number,store_count,driver_id,driver_name) -> int | Dict[str,Any] | None :
    if all(x is None for x in [store_number,store_count,driver_id,driver_name]) or store_number is None:
        print('store_number must be provided and with him driver_id and driver_name')
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

    if driver_name is not None:
        query = query + ' driver_name = ?,'
        parameters.append(driver_name)

    query = query.rstrip(', ') + ' WHERE store_number = ?'
    parameters.append(store_number)
    try:
        with get_connection() as conn:
            cursor = conn.execute(query, (parameters,))
            if cursor.rowcount == 0:
                return 2

    except sqlite3.IntegrityError as e:
        print(str(e))
        return 3

    return get_row_output(store_number)

def delete_row_output(store_number:int) -> bool :
    query = '''
    DELETE FROM output_data WHERE store_number = ?'''
    with get_connection() as conn:
        cursor = conn.execute(query, (store_number,))
        return cursor.rowcount > 0

def delete_output_table()-> bool :
    query = '''
    DELETE TABLE IF EXISTS output_data;'''
    with get_connection() as conn:
        cursor = conn.execute(query)
        return cursor.rowcount > 0





