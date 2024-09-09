import random
from random import randint
from os import environ
from flask import Flask, jsonify, send_file
from pathlib import Path


app = Flask(__name__)


def get_semi_random_uuid(last_char: str = None):
    '''
    Rerurns valid UUID with randomized last character, if parameter is not specified
    :return: Returns UUID as string value
    '''
    ID_PREFIX = "11111111-2222-3333-4444-55555555555"
    last_character = last_char if last_char is not None else str(randint(0, 9))

    return ID_PREFIX + last_character


@app.route("/tasks", methods=['GET'])
def tasks():
    """
    Endpoint for receiving mocked tasks.
    :return: Task's data in JSON format.
    """
    randomized_task: dict = {
        "student_id": str(randint(1, 10)),
        "task_id": get_semi_random_uuid(random.choice(['A', 'B', 'C', 'D', 'E', 'F'])),
        "file_ids": [get_semi_random_uuid() for _ in range(randint(1, 5))]
    }

    return jsonify(randomized_task), 200


@app.route("/files/<file_id>", methods=['GET'])
def files(file_id: str):
    """
    Creates example file, fills it with some data (its id in this case) and returns this as a plaintext.
    :param file_id: Id of the file.
    :return: Invokes send_file function of flask library.
    """
    file_path = str(Path('data.txt'))
    with open( file_path, "w") as randomized_file:
        _ = randomized_file.write(str(file_id))

    return send_file(file_path, as_attachment=True, mimetype="text/plain"), 200


@app.route("/tasks/<task_id>", methods=['POST'])
def task(task_id: str):
    """
    Mock endpoint for submitting task result.
    :param task_id: Id of the task.
    :return: Result message in JSON format.
    """
    return jsonify({"result": "uploaded " + str(task_id)}), 200


PORT = int(environ.get("STOS_PORT", '2137'))
HOST = environ.get("STOS_HOST", '127.0.0.1')
app.run(host=HOST, port=PORT)
