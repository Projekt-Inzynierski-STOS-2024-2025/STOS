from random import randint
from flask import Flask, jsonify, send_file

app = Flask(__name__)


@app.route("/tasks", methods=['GET'])
def tasks():
    randomized_task: dict = {
        "id_studenta": randint(1, 100),
        "id_zadania": randint(1, 100),
        "id_plikow": [randint(1, 20) for _ in range(randint(1, 5))]
    }

    return jsonify(randomized_task), 200


@app.route("/files/<int:file_id>", methods=['GET'])
def files(file_id: int):
    randomized_file = open("data.txt", "w")
    randomized_file.write(str(file_id))

    return send_file("data.txt", as_attachment=True, mimetype="text/plain"), 200


@app.route("/tasks/<int:task_id>", methods=['POST'])
def task(task_id: int):
    return jsonify({"result": "uploaded " + str(task_id)}), 200


app.run(host='0.0.0.0', port=5000)