import os
import sqlite3 as sqlite

from dotenv import load_dotenv

from manager.cache_driver import SQliteCacheDriver
import pytest

@pytest.fixture(scope = 'session', autouse = True)
def connection():
    _ = load_dotenv("./testing.env")
    print(os.environ.get("ENVIRONMENT"))
    db_name = os.environ.get("TEST_DB", "test")+".db"
    connection = sqlite.connect(db_name)
    yield connection
    connection.close()
    os.remove(db_name)


def test_insert(connection):
    path = "/tmp/stos/2137"
    second_path = "/tmp/stos/another"
    file = "2137"
    command = f"SELECT * FROM files WHERE fileId = {file}"

    SQliteCacheDriver.add_entry(file, path)
    cursor = connection.cursor()
    _ = cursor.execute(command)
    res: tuple[int, str, str] | None = cursor.fetchone()
    assert res
    assert res[2] == path
    SQliteCacheDriver.add_entry(file, second_path)
    _ = cursor.execute(command)
    res_second: tuple[int, str, str] | None = cursor.fetchone()
    assert res_second
    assert res_second[2] == second_path

def test_read(connection):
    path = "/tmp/stos/2137"
    file = "89"
    command = """INSERT INTO files(fileId, filePath) VALUES(?, ?)"""

    cursor = connection.cursor()
    _ = cursor.execute(command, [file, path])
    connection.commit()
    assert SQliteCacheDriver.check_files([file]) == []
    assert SQliteCacheDriver.get_entry(file) is not None
    assert SQliteCacheDriver.get_entry(file).disk_path == path
    assert SQliteCacheDriver.get_entry(file).file_id == file

def test_delete(connection):
    path = "/tmp/stos/254"
    file = "254"
    second_file = "255"
    command = """INSERT INTO files(fileId, filePath) VALUES(?, ?)"""
    select_one = """SELECT * FROM files WHERE fileId = ?"""

    cursor = connection.cursor()
    _ = cursor.execute(command, [file, path])
    connection.commit()
    _ = cursor.execute(command, [second_file, path])
    connection.commit()
    SQliteCacheDriver.delete_entry(file)
    _ = cursor.execute(select_one, [file]);
    res: tuple[int, str, str] | None = cursor.fetchone();
    assert res is None
