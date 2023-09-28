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
    try:
        data = dbHandling.read_database(mongo)
        return jsonify(data), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/upload", methods=["POST"])
def recieveFile():
    if "csvFile" not in request.files:
        jsonify({"error": "No file part"}), 400

    recievedFile = request.files["csvFile"]
    if recievedFile.filename == "":
        return "No selected file", 400
    json_data = dataProcessing.process_csv_to_json(recievedFile)
    if json_data:
        dbHandling.add_to_database(mongo, json.loads(json_data))
        return jsonify({"status": "SUCCESS"}), 200
    else:
        return jsonify({"error": "JSON not formatted properly, try again"}), 400


# if __name__ == "__main__":
#     app.run(debug=False, host="0.0.0.0")