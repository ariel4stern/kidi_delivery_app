import json
import sqlite3
from contextlib import contextmanager
from typing import List, Iterator, Tuple, Any ,Dict

DB_NAME = "deliveries_distribution.db"
VALID_DAYS = {'sunday', 'monday', 'tuesday','wednesday', 'thursday', 'friday', 'saturday'}

@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
def validate_distribution_line(day: str, lines: list[int]) -> Tuple[bool,Any] :

    if day not in VALID_DAYS:
        return False,'invalid day'

    if not isinstance(lines, list):
        return False,'not a list'

    if not all(type(num) is int for num in lines):
        return False,'not all integers in list'

    return True,'valid day'

def create_distribution_lines():
    query = '''
    CREATE TABLE IF NOT EXISTS distribution_lines (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        day TEXT NOT NULL UNIQUE,
        distribution_line TEXT NOT NULL DEFAULT '[]'
    );
    '''
    with get_connection() as conn:
        conn.execute(query)
def insert_existing_distribution_lines()->int:
    query = '''INSERT INTO distribution_lines(day,distribution_line) VALUES (?,?)
    ON CONFLICT(day) DO NOTHING;'''
    distribution_lines_dict = {
        'day':['sunday', 'monday', 'tuesday','wednesday', 'thursday', 'friday', 'saturday'],
        'distribution_line':[
            [3,13,23,30,31,36,701,703,706,5,27,20,709,10,18,32,33,37],
            [17,21,24,25,34,39,22,26,1],
            [1,6,9,12,16,43,704,705,11,14,19,29,35,708],
            [3,13,23,30,31,36,701,703,706,5,27,20,709,10,18,32,33,37],
            [1,6,9,12,16,43,704,705,11,14,19,29,35,708,17,21,24,25,34,39,22,26],
            [],
            []
        ]
    }

    distribution_lines_zip = list(zip(
        distribution_lines_dict['day'],
        [
            json.dumps(lines, ensure_ascii=False)
            for lines in distribution_lines_dict['distribution_line']
        ]
    ))

    with get_connection() as conn:
        cursor = conn.executemany(query, distribution_lines_zip)

        return cursor.rowcount
def initialize_delivery_table():
    create_distribution_lines()
    inserted = insert_existing_distribution_lines()

    print(f'Table initialized successfully. {inserted} days added.')

def get_distribution_line(day: str) -> None | Dict[ str, List[str] ] :
    query = '''
    SELECT * FROM distribution_lines WHERE day = ?;
    '''

    with get_connection() as conn:
        row = conn.execute(query, (day,)).fetchone()

        if row is None:
            return None

        result = dict(row)
        result['distribution_line'] = json.loads(result['distribution_line'])

        return result
def get_distribution_lines_table() -> List[Dict[ str, List[str] ]] | [] | None:
    query = '''SELECT * FROM distribution_lines;'''

    try:
        with get_connection() as conn:
            rows = conn.execute(query).fetchall()

            results = []

            for row in rows:
                result = dict(row)
                # print(type(result['distribution_line'])) = str
                result['distribution_line'] = json.loads(
                    result['distribution_line']
                )
                # print(type(result['distribution_line'])) = list
                results.append(result)

            return results

    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            return []
        return None

def update_distribution_line(day:str, distribution_line_l:List[int]) -> Dict[str, List[str]] | None:
    existing = get_distribution_line(day)
    if existing is None:
        return None

    query = '''
    UPDATE distribution_lines 
    SET distribution_line = ? 
    WHERE day = ?;
    '''
    with get_connection() as conn:
        cursor = conn.execute(query, (json.dumps(distribution_line_l), day))
        if cursor.rowcount == 0:
            return None
    return get_distribution_line(day)

def clear_distribution_line(day:str) -> bool:
    done = update_distribution_line(day, [])
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


