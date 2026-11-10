import sqlite3
from contextlib import contextmanager
from typing import List, Dict, Iterator, Any

DB_NAME = "deliveries_distribution.db"

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

def create_table_drivers():
    query = '''
    CREATE TABLE IF NOT EXISTS drivers (
            driver_id INTEGER NOT NULL PRIMARY KEY,
            driver_name TEXT NOT NULL,
            driver_phone TEXT NOT NULL UNIQUE,
            cartoons_count INTEGER NOT NULL DEFAULT 0,
            max_cartoons_count INTEGER NOT NULL DEFAULT 110,
            distribution_area TEXT DEFAULT 'clear' ,
            driver_status TEXT NOT NULL DEFAULT 'not_available'
    );'''
    with get_connection() as conn:
        conn.execute(query)
def insert_existing_drivers() -> int | None :
    drivers_dict = {
        "name" : ['משה','ליאוניד','אוריאל','ישי'],
        "phone": ['050','051','052','053']
    }
    drivers_zip = list(zip(
        drivers_dict['name'],
        drivers_dict['phone']
    ))
    query = '''
        INSERT INTO drivers (driver_name, driver_phone)
        VALUES (?, ?)
    '''
    try:
        with get_connection() as conn:
            cursor = conn.executemany(query, drivers_zip)
            return cursor.rowcount

    except sqlite3.IntegrityError as e:
        print(e)
        return None
def initial_drivers() -> bool:
    create_table_drivers()
    if rows_exists("drivers"):
        print(f'drivers Table already exists.')
        return False

    inserted = insert_existing_drivers()
    print(f'drivers Table initialized successfully. {inserted} new drivers added.')
    return True

def get_driver(driver_id: int) -> Dict[str, Any] | None :
    query = '''
    SELECT * FROM drivers WHERE driver_id = ?;'''
    with get_connection() as conn:
        row = conn.execute(query, (driver_id,)).fetchone()
        if row is None:
            return None
        return dict(row)
def get_all_drivers() -> List[ Dict[str, Any] ] | None :
    query = '''
    SELECT * FROM drivers;'''
    try:
        with get_connection() as conn:
            rows = conn.execute(query).fetchall()
            return [dict(r) for r in rows]
    except sqlite3.OperationalError as e:
        if 'no such table' in str(e):
            return None
        raise
def get_available_drivers() -> List[ Dict[str, Any] ] | None :

    query = '''
    SELECT driver_id,driver_name,cartoons_count FROM drivers WHERE driver_status = ?;'''
    with get_connection() as conn:
        rows = conn.execute(query, ('available',)).fetchall()
        if not rows:
            return None
        return [dict(r) for r in rows]
def get_cartoons_count(driver_id: int) -> int | None:
    query = '''SELECT cartoons_count FROM drivers WHERE driver_id = ?;'''
    with get_connection() as conn:
        row = conn.execute(query, (driver_id,)).fetchone()
        if not row:
            return None
        return row[0]

def insert_driver(d_name:str,d_phone:str) -> Dict[str, Any] | None :
    query = '''
    INSERT INTO drivers (driver_name, driver_phone)
        VALUES ( ?, ?)
    '''
    try:
        with get_connection() as conn:
            cursor = conn.execute(query, (d_name,d_phone))
            if cursor.rowcount == 0:
                return None
            last_id = cursor.lastrowid

            if last_id is None:
                return None

        return get_driver(last_id)

    except sqlite3.IntegrityError as e:
        print(str(e))
        return None

def patch_driver(d_id:int,d_name,d_phone,d_cartoons_count,d_max_cartoons,d_distribution_area,d_status) -> Dict[str, Any] | int | None :
    if all(x is None for x in [d_name,d_phone,d_cartoons_count,d_max_cartoons,
                                d_distribution_area,d_status]):
        return 0

    query = '''
    UPDATE drivers SET'''
    parameters = []

    if d_name is not None:
        query = query + ' driver_name = ?,'
        parameters.append(d_name)

    if d_phone is not None:
        query = query + ' driver_phone = ?,'
        parameters.append(d_phone)

    if d_cartoons_count is not None:
        query = query + ' cartoons_count = ?,'
        parameters.append(d_cartoons_count)

    if d_max_cartoons is not None:
        query = query + ' max_cartoons = ?,'
        parameters.append(d_max_cartoons)

    if d_distribution_area is not None:
        query = query + ' distribution_area = ?,'
        parameters.append(d_distribution_area)

    if d_status is not None:
        query = query + ' driver_status = ?,'
        parameters.append(d_status)

    query = query.rstrip(", ") + ' WHERE driver_id = ?;'
    parameters.append(d_id)
    print(query,parameters)

    try:
        with get_connection() as conn:
            cursor = conn.execute(query, parameters)
            if cursor.rowcount == 0: # rows infected from query
                return 1

    except sqlite3.IntegrityError as e:
        print(str(e))
        return 2

    return get_driver(d_id)

def delete_driver(d_id:int)-> bool:
    query = '''
    DELETE FROM drivers WHERE driver_id = ?;'''
    with get_connection() as conn:
        cursor = conn.execute(query, (d_id,))
        return cursor.rowcount > 0


#create_table_drivers()
#print(get_all_drivers())
#create_table_drivers()
#initial_drivers()


