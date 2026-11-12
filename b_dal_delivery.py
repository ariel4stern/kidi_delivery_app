import json
import sqlite3
from contextlib import contextmanager
from typing import List, Iterator, Tuple, Any ,Dict

DB_NAME = "deliveries_distribution.db"

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

# def validate_distribution_line(day: str, lines: list[int]) -> Tuple[bool,Any] :
#
#     if day not in VALID_DAYS:
#         return False,'invalid day'
#
#     if not isinstance(lines, list):
#         return False,'not a list'
#
#     if not all(type(num) is int for num in lines):
#         return False,'not all integers in list'
#
#     return True,'valid day'

def create_distribution_lines():
    query = '''
    CREATE TABLE IF NOT EXISTS distribution_lines (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        day TEXT NOT NULL UNIQUE,
        stores_numbers TEXT NOT NULL DEFAULT '[]',
        distribution_areas TEXT NOT NULL DEFAULT '[]'
    );
    '''
    with get_connection() as conn:
        conn.execute(query)
def insert_existing_distribution_lines()->int:
    query = '''INSERT INTO distribution_lines(day,stores_numbers,distribution_areas) VALUES (?,?,?)
    ON CONFLICT(day) DO NOTHING;'''
    distribution_lines_dict = {
        'day':['sunday', 'monday', 'tuesday','wednesday', 'thursday', 'friday', 'saturday'],
        'stores_numbers':[
            [3,13,23,30,31,36,701,703,706,5,27,20,709,10,18,32,33,37],
            [17,21,24,25,34,39,22,26,1],
            [1,6,9,12,16,43,704,705,11,14,19,29,35,708],
            [3,13,23,30,31,36,701,703,706,5,27,20,709,10,18,32,33,37],
            [1,6,9,12,16,43,704,705,11,14,19,29,35,708,17,21,24,25,34,39,22,26],
            [],
            []],
        'distribution_areas':[
            ['ירושלים','בית_שמש','ביתר'],
            ['צפון','מודיעין','עזרא'],
            ['בני_ברק','דרום'],
            ['ירושלים','בית_שמש','ביתר'],
            ['בני_ברק','דרום','צפון','מודיעין'],
            [],
            []]

    }

    distribution_lines_zip = list(zip(
        distribution_lines_dict['day'],
        [
            json.dumps(lines, ensure_ascii=False)
            for lines in distribution_lines_dict['stores_numbers']
        ],
        [
            json.dumps(lines, ensure_ascii=False)
            for lines in distribution_lines_dict['distribution_areas']
        ]
    ))

    with get_connection() as conn:
        cursor = conn.executemany(query, distribution_lines_zip)
        return cursor.rowcount

def initialize_delivery_table():
    create_distribution_lines()
    inserted = insert_existing_distribution_lines()

    print(f'Table initialized successfully. {inserted} days added.')

def get_distribution_line(day: str) -> None | Dict[ str, List[str] | List[int] ] :
    query = '''
    SELECT * FROM distribution_lines WHERE day = ?;
    '''

    with get_connection() as conn:
        row = conn.execute(query, (day,)).fetchone()

        if row is None:
            return None

        result = dict(row)
        result['stores_numbers'] = json.loads(result['stores_numbers'])
        result['distribution_areas'] = json.loads(result['distribution_areas'])

        return result
def get_distribution_lines_table() -> List[Dict[str, List[int] | List[str]]] | None:
    query = '''SELECT * FROM distribution_lines;'''

    try:
        with get_connection() as conn:
            rows = conn.execute(query).fetchall()

            results = []

            for row in rows:
                result = dict(row)
                # print(type(result['distribution_line'])) = str
                result['stores_numbers'] = json.loads( # represent int array
                    result['stores_numbers'])
                result['distribution_areas'] = json.loads( # represent str array
                    result['distribution_areas'])
                # print(type(result['distribution_line'])) = list
                results.append(result)

            return results

    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            return []
        return None

def get_today_store_numbers(day:str) -> None | Dict[str,List[int]] :
    query = '''
    SELECT stores_numbers FROM distribution_lines WHERE day = ?;'''
    with get_connection() as conn:
        row = conn.execute(query, (day,)).fetchone()
        if not row:
            return None
        result = dict(row)
        result['stores_numbers'] = json.loads( result['stores_numbers'])
        return result

def patch_distribution_line(day:str, stores_numbers_l:List[int],
            distribution_area_l:List[str]) -> (Dict[str, List[str] | List[int]] | int | None):

    if all(not x for x in [stores_numbers_l, distribution_area_l]):
        return 0

    query = '''
    UPDATE distribution_lines SET'''
    parameters = []

    if stores_numbers_l is not None:
        query = query + f' stores_numbers = ?,'
        parameters.append(json.dumps(stores_numbers_l, ensure_ascii=False))

    if distribution_area_l is not None:
        query = query + f' distribution_areas = ?,'
        parameters.append(json.dumps(distribution_area_l, ensure_ascii=False))

    query = query.rstrip(", ") + f' WHERE day = ?;'
    parameters.append(day)

    try:
        with get_connection() as conn:
            cursor = conn.execute(query, parameters)
            if cursor.rowcount == 0:
                return 1

    except sqlite3.IntegrityError as e:
        print(str(e))
        return 2

    return get_distribution_line(day)

def clear_distribution_line(day:str) -> bool:
    done = patch_distribution_line(day, [],[])
    if not done:
        return False
    return True

def drop_distribution_line_table() -> bool:
    query = '''
    DROP TABLE IF EXISTS distribution_lines;'''

    try:
        with get_connection() as conn:
            conn.execute(query)
            return True

    except sqlite3.OperationalError:
        return False






# initialize_delivery_table()
# print(get_distribution_lines_table())
# print(get_distribution_line('monday'))
# print(get_distribution_line('sunday'))


