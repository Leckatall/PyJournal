import sqlite3
from sqlite3 import Error
import logging, sys

CREATE_ENTRIES_TABLE = """CREATE TABLE IF NOT EXISTS Entries(
                                       id INTEGER PRIMARY KEY,
                                       date TEXT NOT NULL,
                                       topic TEXT NOT NULL,
                                       title TEXT NOT NULL,
                                       content TEXT NOT NULL
                                    );"""


def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

def SQL_connection(**kwargs):
    ...


class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.con = create_connection(db_path)
        self.cur = self.con.cursor()

    def get_row_with_id(self, id, columns, table):
        command_output = self.cur.execute("SELECT " +
                                          columns +
                                          " FROM " +
                                          table +
                                          " WHERE " +
                                          table +
                                          ".id IS " +
                                          str(id)).fetchone()
        if len(command_output) == 1:
            return command_output[0]
        return command_output

    def get(self, columns, table):
        return self.cur.execute("SELECT " + columns + " FROM " + table).fetchall()


class JournalDB:
    def __init__(self):
        DATABASE_PATH = "journal.db"
        self.con = create_connection(DATABASE_PATH)
        self.cur = self.con.cursor()

    def get_entries_for_date(self, date):
        self.cur.execute(f"SELECT * FROM Entries WHERE Entries.date = {date};")

    def get_entries_for_where(self, **kwargs):
        self.cur.execute(f"""SELECT * FROM Entries WHERE {" AND ".join(
            [f"{kwarg_value} = {kwarg_key}" for kwarg_value, kwarg_key in kwargs.values()]
        )
        };""")

    def get_entries_for_topic(self, date):
        self.cur.execute(f"""SELECT * FROM Entries WHERE Entries.date = {date};""")

    def add_entry_for_date(self, date, topic, title, content):
        self.cur.execute(f"INSERT INTO Entries (date, topic, title, content) {date, topic, title, content};")

# DATABASE_PATH = "journal.db"
# con = create_connection(DATABASE_PATH)
# cur = con.cursor()
#
#
# cur.execute(CREATE_ENTRIES_TABLE)
