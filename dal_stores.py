import json
import sqlite3
from contextlib import contextmanager
from idlelib import query

DB_DELIVERY_NAME = "delivery.db"

@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_DELIVERY_NAME)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def create_distribution_lines():
    query = '''
    CREATE TABLE IF NOT EXISTS distribution_lines (
        day TEXT PRIMARY KEY,
        distribution_line TEXT NOT NULL DEFAULT '[]'
    );
    '''
    with get_connection() as conn:
        conn.execute(query)

def insert_existing_distribution_lines():
    query = '''INSERT INTO distribution_lines(day,distribution_line) VALUES (?,?);'''
    distribution_lines_dict = {
        'day':['sunday', 'monday', 'tuesday','wednesday', 'thursday', 'friday', 'saturday'],
        'distribution_line':[
            ['ירושלים','ביתר','בית_שמש'],
            ['צפון','מודיעין','עזרא'],
            ['בני_ברק','דרום'],
            ['ירושלים','ביתר','בית_שמש'],
            ['בני_ברק','דרום','מודיעין','צפון'],
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

    if len(get_distribution_lines_table()) == 0:
        inserted = insert_existing_distribution_lines()
        print(f'Table initialized successfully. {inserted} days added.')
    else:
        print('Table already initialized.')

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
            return [dict(r) for r in rows]


    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            print(e)
            return []
        raise

initialize_delivery_table()
print(get_distribution_lines_table())
