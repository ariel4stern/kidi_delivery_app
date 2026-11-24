import sqlite3
from contextlib import contextmanager
from typing import List, Dict, Iterator, Any

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
    return conn
def rows_exists(table_name:str) -> bool :
    query = f'''SELECT EXISTS(SELECT 1 FROM {table_name});'''
    with get_connection() as conn:
        cursor = conn.execute(query).fetchone()
        return bool(cursor[0])

def create_table_point_distributions() -> None :
    query = '''
    CREATE TABLE IF NOT EXISTS point_distributions (
        driver_id INTEGER DEFAULT 5,
        driver_name TEXT DEFAULT 'nobody',
        day TEXT NOT NULL,
        point INTEGER NOT NULL,
        
        FOREIGN KEY (driver_id)
        REFERENCES drivers(driver_id)
        ON DELETE SET NULL
    );'''

    with get_connection() as conn:
        conn.execute(query)

def insert_point_distributions() -> int | None :
    point_distributions_dict = {
        'driver_id': [2,3,2,2,2,2,3,2,2,1,1,1,1,1,1,1,1,1,
                      1,1,1,1,1,1,2,2,2,
                      1,1,1,1,1,1,1,1,2,2,2,2,2,2,
                      2,2,2,2,2,2,2,2,2,1,1,1,1,1,1,1,1,1,2,2,
                      1,1,1,1,1,1,1,1,2,2,2,2,2,2,3,3,3,3,3,3,
                      5,
                      5],
        'day': ['sunday', 'sunday', 'sunday', 'sunday', 'sunday', 'sunday','sunday', 'sunday', 'sunday',
                'sunday', 'sunday', 'sunday', 'sunday', 'sunday', 'sunday', 'sunday', 'sunday', 'sunday',
                'monday', 'monday', 'monday', 'monday', 'monday', 'monday', 'monday', 'monday', 'monday',
                'tuesday', 'tuesday', 'tuesday', 'tuesday', 'tuesday', 'tuesday', 'tuesday', 'tuesday',
                'tuesday', 'tuesday', 'tuesday', 'tuesday', 'tuesday', 'tuesday',
                'wednesday', 'wednesday', 'wednesday','wednesday', 'wednesday', 'wednesday','wednesday', 'wednesday', 'wednesday',
                'wednesday', 'wednesday', 'wednesday','wednesday', 'wednesday', 'wednesday','wednesday', 'wednesday', 'wednesday',
                'wednesday', 'wednesday',
                'thursday', 'thursday', 'thursday', 'thursday','thursday', 'thursday', 'thursday', 'thursday',
                'thursday', 'thursday', 'thursday', 'thursday','thursday', 'thursday', 'thursday', 'thursday',
                'thursday', 'thursday', 'thursday', 'thursday',
                'friday',
                'saturday'],
        'point': [3,13,23,30,31,36,701,703,706,5,27,20,709,10,18,32,33,37,
                 17,21,24,25,34,39,22,26,1,
                 1,6,9,12,16,43,704,705,11,14,19,29,35,708,
                 3,13,23,30,31,36,701,703,706,5,27,20,709,10,18,32,33,37,22,26,
                 1,6,9,12,16,43,704,705,11,14,19,29,35,708,17,21,24,25,34,39,
                 404,
                 405]


        }
    area_distributions_dict_zip = list(zip(
        point_distributions_dict['driver_id'],
        point_distributions_dict['day'],
        point_distributions_dict['point'],
        ))
    query = '''
        INSERT INTO point_distributions
            (driver_id, driver_name, day, point)
        SELECT ?, driver_name, ?, ?
        FROM drivers
        WHERE driver_id = ?;
        '''
    try:
        with get_connection() as conn:
            data = [
                (driver_id, day, point, driver_id)
                for driver_id, day, point in area_distributions_dict_zip
            ]
            cursor = conn.executemany(query, data)
            if cursor.rowcount == 0:
                return None
            return cursor.rowcount

    except sqlite3.IntegrityError as e:
        print(str(e))
        return None
def initialize_point_distributions() -> bool:
    create_table_point_distributions()
    if rows_exists('point_distributions'):
        print('point_distributions table already exists')
        return False

    inserted = insert_point_distributions()
    print(f'point_distributions table created with {inserted} rows')
    return True

def insert_new_day_point(d_id: int | None ,day: str ,point: int) -> Dict[str ,Any] | int | None :

    with get_connection() as conn:

        if d_id is not None:
            driver = conn.execute(
                'SELECT driver_name FROM drivers WHERE driver_id = ?',
                (d_id,)
            ).fetchone()
            print(driver[0])
            if driver is None:
                return 0

            query = '''
            INSERT INTO point_distributions
                (driver_id, driver_name, day, point)
            VALUES (?, ?, ?, ?);
            '''

            parameters = (d_id, driver[0], day, point)

        else:
            query = '''
            INSERT INTO point_distributions (day, point)
            VALUES (?, ?);
            '''

            parameters = (day, point)

        try:
            cursor = conn.execute(query, parameters)

            if cursor.rowcount == 0:
                return 1

        except sqlite3.IntegrityError as e:
            print(str(e))
            return 2

    return get_dist_point(day, point)

def get_all_dist_point() -> List[Dict[str,Any]] | None :
    query = '''
    SELECT * FROM point_distributions'''
    with get_connection() as conn:
        rows = conn.execute(query).fetchall()
        if not rows:
            return None
        return [dict(row) for row in rows]

def get_dist_point(day:str ,point:int) -> Dict[str,Any] | None :
    query = '''
    SELECT driver_id, driver_name, day, point
    FROM point_distributions
    WHERE (day = ? AND point = ?);
    '''

    with get_connection() as conn:
        row = conn.execute(query, (day, point,)).fetchone()

        if not row:
            return None

        return dict(row)

def update_day_point(d_id,day,point) -> int | Dict[str,Any] | None :
    query = '''
    UPDATE point_distributions SET 
    driver_id = ?,
    driver_name=(SELECT driver_name FROM drivers WHERE driver_id = ?)
    WHERE day = ? AND point = ?;'''

    with get_connection() as conn:
        cursor = conn.execute(query, (d_id,d_id, day, point))
        if cursor.rowcount == 0:
            return 0
    return get_dist_point(day,point)

def delete_day_point(day:str,point:int) -> bool :
    query = '''
    DELETE FROM point_distibutions WHERE day = ? AND point = ?'''
    with get_connection() as conn:
        cursor = conn.execute(query, (day, point))
        return cursor.rowcount > 0


