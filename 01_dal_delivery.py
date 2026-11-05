import json
import sqlite3
from contextlib import contextmanager
from typing import List

DB_DELIVERY_NAME = "delivery.db"
VALID_DAYS = {'sunday', 'monday', 'tuesday','wednesday', 'thursday', 'friday', 'saturday'}
@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_DELIVERY_NAME)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def validate_distribution_line(day: str, lines: list[int]):

    if day not in VALID_DAYS:
        raise ValueError(f'Invalid day: {day}')

    if not isinstance(lines, list):
        raise TypeError('distribution_line must be a list')

    if not all(type(num) is int for num in lines):
        raise TypeError('All distribution line values must be integers')

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
def insert_existing_distribution_lines():
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

def get_distribution_line(day: str):
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
def get_distribution_lines_table():
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
        raise

def insert_distribution_line(day: str, distribution_line: List[int]):
    query = '''INSERT INTO distribution_lines(day,distribution_line)
                 VALUES (?,?)
                 ON CONFLICT (day) DO NOTHING;'''

    with get_connection() as conn:
        cursor = conn.execute(query, ( day,json.dumps(distribution_line,ensure_ascii=False)))
        return cursor.rowcount

def update_distribution_line(day:str, distribution_line_l:List[int]):
    existing = get_distribution_line(day)
    if existing is None or not distribution_line_l:
        return None

    query = '''
    UPDATE distribution_lines 
    SET distribution_line = ? 
    WHERE day = ?;
    '''
    with get_connection() as conn:
        cursor = conn.execute(query, (json.dumps(distribution_line_l), day))
        return cursor.rowcount > 0

def clear_distribution_line(day:str):
    done = update_distribution_line(day, [])
    if not done:
        return None
    return f'day: {day} cleared'






# initialize_delivery_table()
# print(get_distribution_lines_table())
# print(get_distribution_line('monday'))
# print(get_distribution_line('sunday'))


