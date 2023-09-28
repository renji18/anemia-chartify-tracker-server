from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from dotenv import load_dotenv
import os
import json
import dataProcessing
import dbHandling
load_dotenv()


app = Flask(__name__)
CORS(app)

app.config["MONGO_URI"] = os.getenv("MONGO_URI")

mongo = PyMongo(app)


@app.route("/", methods=["GET"])
def hello():
    data = dbHandling.read_database(mongo)
    if data:
        return jsonify(data), 201
    else:
        return "ERROR COMMUNICATING TO DATABASE"


@app.route("/upload", methods=["POST"])
def recieveFile():
    if "csvFile" not in request.files:
        return "No file part", 400

    recievedFile = request.files["csvFile"]
    if recievedFile.filename == "":
        return "No selected file", 400
    json_data = dataProcessing.process_csv_to_json(recievedFile)
    if json_data:
        return dbHandling.add_to_database(mongo, json.loads(json_data))
    else:
        return "JSON not formatted properly, try again"


# if __name__ == "__main__":
#     app.run(debug=False, host="0.0.0.0")
