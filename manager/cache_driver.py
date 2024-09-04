from abc import ABC, abstractmethod
from os import environ
from typing import override
import sqlite3 as sqlite

from manager.types import TaskFile, TaskFileType


class ICacheDriver(ABC):

    # Checks cache for existance of files and returns missing files
    @staticmethod
    @abstractmethod
    def check_files(files: list[str]) -> list[str]:
        pass

    # Adds entry regarding a single file to cache and overwrites old record
    @staticmethod
    @abstractmethod
    def add_entry(file: str, path: str):
        pass

    # Deletes a record representing file
    @staticmethod
    @abstractmethod
    def delete_entry(file: str):
        pass

    # Get file entry, returns None if file does not exist
    @staticmethod
    @abstractmethod
    def get_entry(file: str) -> TaskFile | None:
        pass



class SQliteCacheDriver(ICacheDriver):

    # Do not access directly, please use __get_connection()
    __connection: sqlite.Connection | None = None

    __use_cache: bool = False if environ.get("USE_CACHE", "False") else True 

    @override
    @staticmethod
    def check_files(files: list[str]) -> list[str]:
        if SQliteCacheDriver.__use_cache:
            missing: list[str] = []
            for file_id in files:
                if SQliteCacheDriver.get_entry(file_id) is None:
                    missing.append(file_id)
            return missing
        return files

    @staticmethod
    @override
    def add_entry(file: str, path: str):
        sql_insertable = [file, path]
        command = """INSERT INTO files (fileId, filePath) VALUES(?, ?)"""
        conn = SQliteCacheDriver.__get_connection()
        if SQliteCacheDriver.get_entry(file) is not None:
            SQliteCacheDriver.delete_entry(file)
        cursor = conn.cursor()
        _ = cursor.execute(command, sql_insertable)
        conn.commit()
        return

    @staticmethod
    @override
    def delete_entry(file: str):
        command = """DELETE FROM files WHERE fileId = ?"""
        conn = SQliteCacheDriver.__get_connection()
        cursor = conn.cursor()
        _ = cursor.execute(command, [file])
        conn.commit()

    @staticmethod
    @override
    def get_entry(file: str) -> TaskFile | None:
        command = """SELECT filePath FROM files WHERE fileId = ? LIMIT 1"""
        conn = SQliteCacheDriver.__get_connection()
        cursor = conn.cursor()
        _ = cursor.execute(command, [file])
        res: tuple[str] | None = cursor.fetchone()
        if res:
            return TaskFile(file, res[0], TaskFileType.STUDENT_FILE)
        else:
            return None

    @staticmethod
    def __get_connection() -> sqlite.Connection:
        if SQliteCacheDriver.__connection is None:
            SQliteCacheDriver.__initialize_sqlite_connection()
        return SQliteCacheDriver.__connection
            

    @staticmethod
    def __initialize_sqlite_connection():
        try:
            db_name = SQliteCacheDriver.__get_database_name()
            connection = sqlite.connect(db_name)
        except sqlite.Error as e:
            print(e)
            exit(-1)
        finally:
            SQliteCacheDriver.__connection = connection
            SQliteCacheDriver.__execute_startup_script()

    @staticmethod
    def __get_database_name():
        env = environ.get("ENVIRONMENT", 'dev')
        if env == "test":
            return environ.get("TEST_DB", "test") + ".db"
        else:
            return environ.get("DB", "cache") + ".db"


    
    @staticmethod
    def __execute_startup_script():
        conn = SQliteCacheDriver.__get_connection()
        commands = ["""
                    CREATE TABLE IF NOT EXISTS files (
                        id INTEGER PRIMARY KEY,
                        fileId text NOT NULL,
                        filePath text NOT NULL
                        )
                    """,
                    """
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_file_id
                    ON files (fileId)
                    """]
        cursor = conn.cursor()
        for command in commands:
            _ = cursor.execute(command)
        conn.commit()
