import sqlite3

with sqlite3.connect("database.db", check_same_thread=False) as connection:
    cursor = connection.cursor()
    
    sqlite_start_commands = (
        
        # "ALTER TABLE mms ADD greatness integer;",
        # "ALTER TABLE mms ADD bio text",
        "UPDATE net SET free_deals = 100 WHERE id = 1032156461",
        'DROP TABLE IF EXISTS donations',
        'UPDATE net SET is_trusted = 0 WHERE is_trusted = ""',
        'CREATE TABLE IF NOT EXISTS delations(topic_id int, initiator int)',
        "PRAGMA encoding='UTF-8'",
        'ALTER TABLE mms DROP COLUMN channel',
        'ALTER TABLE mms DROP COLUMN searches',
        'ALTER TABLE mms DROP COLUMN state',
        "ALTER TABLE net ADD contribution integer DEFAULT 0",
        'ALTER TABLE mms DROP COLUMN bio',
        'ALTER TABLE mms DROP COLUMN greatness',
        # "ALTER TABLE net ADD picture text",
        # "ALTER TABLE net ADD is_trusted integer DEFAULT 0",
        # "ALTER TABLE net ADD was_in_db integer DEFAULT 0",
        # "ALTER TABLE admins ADD dob integer",
        # "ALTER TABLE groups ADD ban integer",
        # "ALTER TABLE groups ADD alert integer",
        # "ALTER TABLE groups ADD help integer",
        # "ALTER TABLE admins ADD warns integer",
        # "ALTER TABLE admins ADD status integer",
        # "ALTER TABLE stats ADD bot text",
        """
        CREATE TABLE IF NOT EXISTS usernames (id int, username text)""",
        """CREATE TABLE IF NOT EXISTS daily_productivity (
                    id integer,
                    productivity integer
                )""",
        """CREATE TABLE IF NOT EXISTS daily_searches (
                    id integer,
                    searches integer
                )""",
        """CREATE TABLE IF NOT EXISTS scammers (
        id integer PRIMARY KEY,
        searches integer,
        reputation text,
        description text
    )""", """CREATE TABLE IF NOT EXISTS mms (
        id integer
    )""", """CREATE TABLE IF NOT EXISTS admins (
        id integer
    )""", """CREATE TABLE IF NOT EXISTS users (
        id integer,
        active integer
    )""", """CREATE TABLE IF NOT EXISTS stats (
        searches integer
    )""",
        """CREATE TABLE IF NOT EXISTS groups (
            id integer,
            active integer
    )""",
        """CREATE TABLE IF NOT EXISTS net (
            id integer,
            searches integer,
            bio text
    )"""
    )
    
    
    
    
    def sql_edit(command, args):
        print('fired')
        try:
            s_c = connection.cursor()
            s_c.execute(command, args)
            connection.commit()
            print('committed')
        except Exception as exc:
            connection.rollback()
            print(f"{command}\nrollback: {exc}")
    
    
    def sql_select(command):
        try:
            s_c = connection.cursor()
            s_c.execute(command)
            return s_c.fetchall()
        except Exception as exc:
            print(f"{command}\nsql_select() error: {exc}")


async def antiflood(*args, **kwargs):
    m = args[0]
    await m.answer("🚫 Прекрати флудить и подожди 5 секунд.")


scam_list = ['scam', 'скам', 'кидок', 'обман', 'взломщик', 'взломал', 'развод', 'кидала']
sus_list = ['раздача петов']

support_symbols = ['△', '∆', '⃤', '▲', '🔺']
