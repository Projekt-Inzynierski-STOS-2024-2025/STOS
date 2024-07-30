from random import randint
from os import environ
from flask import Flask, jsonify, send_file

app = Flask(__name__)


@app.route("/tasks", methods=['GET'])
def tasks():
    """
    Endpoint for receiving mocked tasks.
    :return: Task's data in JSON format.
    """
    randomized_task: dict = {
        "student_id": str(randint(1, 100)),
        "task_id": str(randint(1, 100)),
        "file_ids": [str(randint(1, 20)) for _ in range(randint(1, 5))]
    }

    return jsonify(randomized_task), 200


@app.route("/files/<file_id>", methods=['GET'])
def files(file_id: str):
    """
    Creates example file, fills it with some data (its id in this case) and returns this as a plaintext.
    :param file_id: Id of the file.
    :return: Invokes send_file function of flask library.
    """
    with open("data.txt", "w") as randomized_file:
        randomized_file.write(str(file_id))

    return send_file("data.txt", as_attachment=True, mimetype="text/plain"), 200


@app.route("/tasks/<task_id>", methods=['POST'])
def task(task_id: str):
    """
    Mock endpoint for submitting task result.
    :param task_id: Id of the task.
    :return: Result message in JSON format.
    """
    return jsonify({"result": "uploaded " + str(task_id)}), 200


PORT = int(environ["STOS_PORT"])
app.run(host='0.0.0.0', port=PORT)
