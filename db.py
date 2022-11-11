from mysql.connector import connect, Error
from os import getenv
from dotenv import load_dotenv
from pathlib import Path


class DB:
    _user = None
    _password = None
    _host = None
    _port = None
    _database = None
    _connection = None
    _cursor = None
    
    def __init__(self) -> None:
        load_dotenv(verbose=False)
        env_path = Path('./env') / '.env'
        load_dotenv(dotenv_path=str(env_path))

        self._user = getenv("DB_USER")
        self._password = getenv("DB_PASSWORD")
        self._host = getenv("DB_HOST")
        self._port = getenv("DB_PORT")
        self._database = getenv("DB_DATABASE")

        try:
            self._connection = connect(
                user=self._user,
                password=self._password,
                host=self._host,
                port=self._port,
                database=self._database
            )
            self._connection.ping(reconnect=True, attempts=3, delay=5)
            self._cursor = self._connection.cursor(buffered=True)
        except Error as e:
            print(">>>", e)

    def __del__(self) -> None:
        self._connection.close()

    def execute(self, query: str, params: tuple = ()) -> None:
        self._cursor.execute(query, params)
        self._connection.commit()

    def fetch(self, query: str, params: tuple = ()) -> list:
        self._cursor.execute(query, params)
        return self._cursor.fetchall()

    def fetch_one(self, query: str, params: tuple = ()) -> tuple:
        self._cursor.execute(query, params)
        return self._cursor.fetchone()

    def get_last_row_id(self) -> int:
        return self._cursor.lastrowid

    def get_row_count(self) -> int:
        return self._cursor.rowcount
