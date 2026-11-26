import sqlite3
from contextlib import contextmanager
from typing import List, Dict, Iterator, Any

DB_NAME = "deliveries_distribution.db"

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

def create_output_table_two() -> None:
    query = '''
        CREATE TABLE IF NOT EXISTS output_data_two (
            store_number REAL PRIMARY KEY,
            store_count INTEGER DEFAULT 0,
            driver_id INTEGER DEFAULT null,
            driver_name TEXT DEFAULT null,
            note TEXT DEFAULT null,

            FOREIGN KEY (driver_id)
            REFERENCES drivers (driver_id)
            ON DELETE SET NULL
            );'''
    with get_connection() as conn:
        conn.execute(query)

def get_row_output_two(store_number:float) -> Dict[str,Any] | None :
    query = '''
    SELECT * FROM output_data_two WHERE store_number = ?'''
    with get_connection() as conn:
        row = conn.execute(query, (store_number,)).fetchone()
        if row is None:
            return None
        return dict(row)
def get_all_rows_output_two() -> List[Dict[str,Any]] | None :
    query = '''
    SELECT store_number, store_count, driver_id, driver_name FROM output_data_two
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

def insert_row_output_two(store_number:float, store_count:int, driver_id ,note) -> Dict[str,Any] | int | None :
    try:
        with get_connection() as conn:
            if driver_id is not None:

                query = '''
                INSERT INTO output_data_two (store_number, store_count, driver_id , note, driver_name )
                VALUES (?, ?, ? ,?,?)
                '''

                parameters = [store_number, store_count, driver_id,note]
                select_query = '''
                SELECT driver_name FROM drivers WHERE driver_id = ?'''

                cursor = conn.execute(select_query, (driver_id,)).fetchone()
                if cursor is None:
                    return 1

                driver_name = str(cursor[0])
                parameters.append(driver_name)
            else:
                query = '''INSERT INTO output_data_two (store_number, store_count,note)
                VALUES (?, ?,?)
                '''
                parameters = [store_number, store_count,note]

            cursor2 = conn.execute(query, parameters)
            if cursor2.rowcount == 0:
                return 2

        return get_row_output_two(store_number)

    except sqlite3.IntegrityError as e:
        print(str(e))
        return 3

def patch_output_row_two(store_number,store_count,driver_id,note) -> int | Dict[str,Any] | None:
    if all(not x for x in [store_count,driver_id,note]):
        print('store_number must be provided and with him driver_id')
        return 0

    existing_row = get_row_output_two(store_number)
    if existing_row is None:
        print('Not such row in output table')
        return 1

    query = '''
    UPDATE output_data_two SET'''
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

    if note is not None:
        query = query + ' note = ?,'
        parameters.append(note)

    query = query.rstrip(', ') + ' WHERE store_number = ?'
    parameters.append(int(store_number))

    with get_connection() as conn:
        cursor = conn.execute(query, parameters)
        if cursor.rowcount == 0:
            return 2

    return get_row_output_two(store_number)

def update_output_two_number(st_number:float,d_id:int) -> float | int :
    query = '''
    UPDATE output_data_two SET
        driver_id = ?,
        driver_name  = (SELECT driver_name FROM drivers WHERE driver_id = ?)
    WHERE store_number = ?
    '''
    try:
        with get_connection() as conn:
            cursor = conn.execute(query, (d_id,d_id,st_number))
            if cursor.rowcount == 0:
                return 0


    except sqlite3.IntegrityError as e:
        print(str(e))
        return 0

    return st_number

def delete_output_table_two()-> bool :
    query = '''
    DELETE FROM output_data_two;'''
    with get_connection() as conn:
        cursor = conn.execute(query)
        if cursor.rowcount == 0:
            return False
        create_output_table_two()
        return True
