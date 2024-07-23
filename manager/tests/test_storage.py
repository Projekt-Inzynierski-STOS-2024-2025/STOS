import os
from manager.storage_driver import LocalStorageDriver


def test_save():
    id = "3"
    content = "Some text"

    path = LocalStorageDriver.save_file(id, content)

    assert path == f"/tmp/stos/{id}"
    assert os.path.isfile(path)

    with open(path, 'r') as saved_file:
        saved_contents = saved_file.read()

    assert content == saved_contents

def test_read():
    id = "4"
    content = "Some text to read"
    path = f"/tmp/stos/{id}"

    with open(path, 'w') as file:
        _ = file.write(content)

    read_content = LocalStorageDriver.get_file(path)
    assert content == read_content
