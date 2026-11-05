import sqlite3
from contextlib import contextmanager

DB_NAME = "stores.db"

@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def create_store_table():
    query = '''CREATE TABLE IF NOT EXISTS stores (store_number INTEGER PRIMARY KEY,
                                                  store_name TEXT UNIQUE NOT NULL,
                                                  store_area TEXT NOT NULL);'''
    with get_connection() as conn:
        conn.execute(query)
def insert_existing_stores():
    query = '''INSERT INTO stores(store_number,store_name,store_area) VALUES (?,?,?)'''
    stores_dict = {
        "number": [1, 3, 5, 6, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 29, 30, 31,
                   32, 33, 34, 35, 36, 37, 39, 43, 701, 703, 704, 705, 706, 707, 708, 709],
        "name": ['עזרא', 'שמגר', 'ביתר', 'אורחות', 'צמרת', 'לב', 'ישועת_חיים', 'מכבי', 'כיכר', 'רחובות',
                 'דובק', 'חיפה', 'הרובע', 'אלעד', 'קריית_אתא', 'בן_דוד', 'ברכפלד', 'כנפי_נשרים', 'טבריה', 'נתניה',
                 'קסם', 'אלואל', 'נתיבות_עודפים', 'אהליאב', 'שנלר', 'אמוראים', 'השדרה', 'חריש', 'נתיבות_סנטר',
                 'רמות', 'בית_שמש_עודפים', 'הרצל', 'כהנמן', 'שפע', 'מלחה', 'רימונים', 'עקיבא', 'שמגר_אווניו',
                 'השדרה_מלאנז', 'אשדוד', 'ביתר_מלאנז'],
        "area": ['בני_ברק', 'ירושלים', 'ביתר', 'בני_ברק', 'בני_ברק', 'בית_שמש', 'דרום', 'בני_ברק', 'ירושלים', 'דרום',
                 'בני_ברק', 'צפון', 'בית_שמש', 'דרום', 'ביתר', 'צפון', 'מודיעין', 'ירושלים', 'צפון', 'צפון',
                 'מודיעין', 'ביתר', 'דרום', 'ירושלים', 'ירושלים', 'בית_שמש', 'בית_שמש', 'צפון', 'דרום',
                 'ירושלים', 'בית_שמש', 'צפון', 'בני_ברק', 'ירושלים', 'ירושלים', 'בני_ברק', 'בני_ברק', 'ירושלים',
                 'בית_שמש', 'דרום', 'ביתר']
    }
    stores = list(zip(
        stores_dict["number"],
        stores_dict["name"],
        stores_dict["area"]

    ))

    with get_connection() as conn:
        cursor = conn.executemany(query,stores)
        return cursor.rowcount
def initial_stores():
    if len(get_store_table()) == 0:
        create_store_table()
        inserted = insert_existing_stores()
        print(f'Stores initialized successfully. {inserted} new stores added.')
    else:
        print(f'Table already exists!')

def get_store_table():
    query = '''SELECT * FROM stores;'''

    try:
        with get_connection() as conn:
            rows = conn.execute(query).fetchall()
            return [dict(r) for r in rows]


    except sqlite3.OperationalError as e:
        if "no such table" in str(e):
            print(e)
            return []
        raise
def get_store(store_number):
    query = '''SELECT * FROM stores WHERE store_number = ?;'''
    with get_connection() as conn:
        row = conn.execute(query, (store_number,)).fetchone()
        return dict(row) if row is not None else None

def insert_new_store(store_number_f, store_name_f,store_area_f):
    query = '''INSERT INTO stores(store_number,store_name,store_area) VALUES (?,?,?)'''
    try:
        with get_connection() as conn:
            conn.execute(query, (store_number_f, store_name_f,store_area_f))
        return get_store(store_number_f)

    except sqlite3.IntegrityError:
        print(f'Store number: [{store_number_f}], or Store name: [{store_name_f}] already exists!')
        return None

def patch_store_table(store_number:int,store_name=None,store_area=None):
    if store_name is None and store_area is None:
        return 'Failure, Not enough store details'

    existing_store = get_store(store_number)
    if existing_store is None:
        return None

    query = '''UPDATE stores SET '''
    parameters = []

    if store_name is not None:
        query = query + f'store_name = ?, '
        parameters.append(store_name)

    if store_area is not None:
        query = query + f'store_area = ?,'
        parameters.append(store_area)

    query = query.rstrip(", ") + ' WHERE store_number = ?;'
    parameters.append(store_number)


    try:
        with get_connection() as conn:
            cursor = conn.execute(query, parameters)
            if cursor.rowcount == 0:
                return None

    except Exception as e:
        print(e)
        return None

    return get_store(store_number)


def delete_store(store_number):
    query = '''DELETE FROM stores WHERE store_number = ?;'''
    with get_connection() as conn:
        cursor = conn.execute(query, (store_number,))

        if cursor.rowcount == 0:
            return None

        return store_number



