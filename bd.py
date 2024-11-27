import sqlite3 as sl


def start_bd():
    global con
    con = sl.connect('Base', check_same_thread=False)


def create_bd():
    try:
        with con:
            con.execute("""
                CREATE TABLE USER (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    Q TEXT,
                    q_poz TEXT
                );
            """)
        print('[LOGS] | I will create USER_DB')
    except:
        print('[ LOGS ] | USER_DB already exists!')
    try:
        with con:
            con.execute("""
                CREATE TABLE QUIZ (
                    id INTEGER PRIMARY KEY,
                    Quiz_id TEXT,
                    questions TEXT,
                    answer_1 TEXT,
                    answer_2 TEXT,
                    answer_3 TEXT,
                    answer_4 TEXT,
                    true_answer TEXT
                );
            """)
        print('[LOGS] | I will create Quiz_DB')
    except:
        print('[ LOGS ] | Quiz_DB already exists!')


def register_user(id='Null', username='Null', Q=bool, q_poz=int):
    try:
        con.execute('INSERT INTO USER (id, name, Q, q_poz) VALUES (?, ?, ?, ?)', [id, username, Q, q_poz])
        con.commit()
        return True
    except sl.Error as e:
        print(f"Ошибка при регистрации пользователя: {e}")
        return False


def get_info(table, where, value=None, what="*"):
    with con:
        cursor = con.cursor()
        cursor.execute(f"SELECT {what} FROM {table} WHERE {where} == {value}")
        records = cursor.fetchall()
        cursor.close()
    try:
        return records
    except:
        return False


def check_register(id=None):
    if get_info("USER", "id", id, "*"):
        return True
    else:
        return False


def get_all(table, what="*"):
    with con:
        cursor = con.cursor()
        cursor.execute(f"SELECT {what} FROM {table}")
        records = cursor.fetchall()
        cursor.close()
    try:
        return records
    except:
        return False


def update(into, what, where):
    con.execute(f'UPDATE USER SET {into} = "{what}" WHERE {where} == id')
    con.commit()
