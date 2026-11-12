import sqlite3
from contextlib import contextmanager
from typing import List, Dict, Iterator, Any

DB_NAME = 'deliveries_distribution.db'

@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
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
    return conn
def rows_exists(table_name:str) -> bool :
    query = f'''SELECT EXISTS(SELECT 1 FROM {table_name});'''
    with get_connection() as conn:
        cursor = conn.execute(query).fetchone()
        return bool(cursor[0])
def create_table_area_distibutions():
    query = '''
    CREATE TABLE IF NOT EXISTS area_distibutions (
        driver_id INTEGER NOT NULL,
        driver_name TEXT NOT NULL,
        day TEXT NOT NULL,
        area_dist TEXT NOT NULL,
    
        PRIMARY KEY (driver_id, driver_name, day, area_dist),
    
        FOREIGN KEY (driver_id)
        REFERENCES drivers(driver_id)
        ON DELETE CASCADE
    );'''

    with get_connection() as conn:
        conn.execute(query)

def insert_area_distributions() -> int | None:
    area_distributions_dict = {
        'driver_id': [1] * 17,
        'name': ['משה'] * 17,
        'day': ['sunday', 'sunday', 'sunday', 'monday', 'monday', 'monday', 'tuesday', 'tuesday',
                'wednesday', 'wednesday', 'wednesday', 'thursday', 'thursday', 'thursday', 'thursday', 'friday',
                'saturday'],
        'area': ['ירושלים', 'בית_שמש', 'ביתר', 'צפון', 'מודיעין', 'עזרא', 'בני_ברק', 'דרום', 'ירושלים', 'בית_שמש',
                 'ביתר',
                 'בני_ברק', 'דרום', 'צפון', 'מודיעין', 'clear', 'clear']
    }
    area_distributions_dict_zip = list(zip(
        area_distributions_dict['driver_id'],
        area_distributions_dict['name'],
        area_distributions_dict['day'],
        area_distributions_dict['area'],
        ))

    query = '''
    INSERT INTO area_distibutions (driver_id ,driver_name ,day ,area_dist) VALUES (?, ?, ?, ?)'''
    try:
        with get_connection() as conn:
            cursor = conn.execute(query, area_distributions_dict_zip)
            return cursor.rowcount > 0

    except sqlite3.IntegrityError as e:
        print(str(e))
        return None
def initialize_area_distributions() -> bool:
    create_table_area_distibutions()
    if rows_exists('area_distibutions'):
        print('area_distibutions table already exists')
        return False
    inserted = insert_area_distributions()
    print(f'area_distibutions table created with {inserted} rows')
    return True

def insert_new_day(d_id:int,day:str, area_dist:str) -> None | Dict[str,Any]:
    query = f'''
    INSERT INTO area_distibutions (driver_id,driver_name,day, area_dist,) SELECT driver_id,driver_name,?,? FROM
    drivers WHERE driver_id =  ?'''
    with get_connection() as conn:
        cursor = conn.execute(query, (day, area_dist, d_id))
        if cursor.rowcount == 0:
            return None

    return get_dist_point(day,area_dist)

def get_all_dist_point() -> List[Dict[str,Any]] | None:
    query = '''
    SELECT driver_id, driver_name,day,area_dist FROM area_distibutions'''
    with get_connection() as conn:
        rows = conn.execute(query).fetchall()
        if not rows:
            return None
        return [dict(row) for row in rows]
def get_dist_point(day:str ,area:str) -> Dict[str,Any] | None:
    query = f'''
    SELECT driver_id,driver_name,day, area_dist  FROM area_distibutions WHERE day = ? AND area_dist = ?'''
    with get_connection() as conn:
        row = conn.execute(query, (day,)).fetchone()
        if not row:
            return None
        return dict(row)

def update_day_area(d_id,day,area_dist) -> None | Dict[str,Any]:
    query = '''
    UPDATE area_distibutions SET d_id = ? WHERE day = ? AND area_dist = ?'''
    with get_connection() as conn:
        cursor = conn.execute(query, (d_id, day, area_dist))
        if cursor.rowcount == 0:
            return None
    return get_dist_point(day,area_dist)

def delete_day_area(day,area) -> bool:
    query = '''
    DELETE FROM area_distibutions WHERE day = ? AND area_dist = ?'''
    with get_connection() as conn:
        cursor = conn.execute(query, (day, area))
        return cursor.rowcount > 0


