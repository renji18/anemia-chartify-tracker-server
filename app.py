from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os
import json
import dataProcessing
import dbHandling
import dataExtractor

load_dotenv()


app = Flask(__name__)
CORS(app)

app.config["MONGO_URI"] = os.getenv("MONGO_URI")

mongo = PyMongo(app)
bcrypt = Bcrypt(app)


# route to retrieve data
@app.route("/", methods=["GET"])
def getData():
    try:
        type = request.args.get("type")
        data = dbHandling.read_database(mongo, type)
        return jsonify(data), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# route for user login
@app.route("/login", methods=["POST"])
def loginUser():
    loggedIn = dbHandling.login_user(mongo, bcrypt, request.json)
    if loggedIn == "Invalid Password":
        return jsonify({"error": "Invalid password"}), 401
    elif loggedIn == "User Logged In Successfully":
        return jsonify({"success": "User logged in successfully"}), 201
    elif loggedIn == "User Not Found":
        return jsonify({"error": "User not found"}), 404
    else:
        return jsonify({"error": "Error connecting to database"}), 400


# route for user registration
@app.route("/register", methods=["POST"])
def registerUser():
    registered = dbHandling.register_user(mongo, bcrypt, request.json)
    if registered == "success":
        return jsonify({"success": "SUCCESS"}), 201
    elif registered == "Username already exists":
        return jsonify({"error": "User already exists"}), 401
    else:
        return jsonify({"error": "Error connecting to database"}), 400


# route to recieve and process uploaded files
@app.route("/upload", methods=["POST"])
def recieveFile():
    if "csvFile" not in request.files:
        jsonify({"error": "No file part"}), 404
    recievedFile = request.files["csvFile"]
    if recievedFile.filename == "":
        return "No selected file", 401
    type = request.form["type"]
    json_data = dataProcessing.process_csv_to_json(recievedFile)
    if json_data:
        dbHandling.add_to_database(mongo, json.loads(json_data), type)
        return jsonify({"status": "SUCCESS"}), 200
    else:
        return jsonify({"error": "JSON not formatted properly, try again"}), 400


# route to download data into excel
@app.route("/download", methods=["GET"])
def exportFile():
    try:
        data = dataExtractor.read_database(mongo)
        print(data)
        response = dataExtractor.modifyToExcel(data)
        return response, 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")
