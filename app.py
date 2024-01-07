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

# Load environment variables from a .env file
load_dotenv()

# Initialize the Flask app
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for all routes

# Configure the app to use MongoDB
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
mongo = PyMongo(app)  # Create a PyMongo instance to interact with MongoDB
bcrypt = Bcrypt(app)  # Create a Bcrypt instance for password hashing


# Route to retrieve data based on the provided 'type' parameter (monthly or quarterly)
@app.route("/", methods=["GET"])
def getData():
    try:
        type = request.args.get("type")
        data = dbHandling.read_database(
            mongo, type
        )  # Call function to read data from MongoDB
        return jsonify(data), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route for user login
@app.route("/login", methods=["POST"])
def loginUser():
    loggedIn = dbHandling.login_user(
        mongo, bcrypt, request.json
    )  # Call function to validate user login
    if loggedIn == "Invalid Password":
        return jsonify({"error": "Invalid password"}), 401
    elif loggedIn == "User Logged In Successfully":
        return jsonify({"success": "User logged in successfully"}), 201
    elif loggedIn == "User Not Found":
        return jsonify({"error": "User not found"}), 404
    else:
        return jsonify({"error": "Error connecting to database"}), 400


# Route for user registration
@app.route("/register", methods=["POST"])
def registerUser():
    registered = dbHandling.register_user(
        mongo, bcrypt, request.json
    )  # Call function to register a new user
    if registered == "success":
        return jsonify({"success": "SUCCESS"}), 201
    elif registered == "Username already exists":
        return jsonify({"error": "User already exists"}), 401
    else:
        return jsonify({"error": "Error connecting to database"}), 400


# Route to receive and process uploaded CSV files
@app.route("/upload", methods=["POST"])
def receiveFile():
    if "csvFile" not in request.files:
        return jsonify({"error": "No file part"}), 404

    receivedFile = request.files["csvFile"]
    if receivedFile.filename == "":
        return "No selected file", 401

    type = request.form["type"]
    json_data = dataProcessing.process_csv_to_json(receivedFile)  # Convert CSV to JSON
    if json_data:
        dbHandling.add_to_database(
            mongo, json.loads(json_data), type
        )  # Add data to MongoDB
        return jsonify({"status": "SUCCESS"}), 200
    else:
        return jsonify({"error": "JSON not formatted properly, try again"}), 400


# Route to download data in Excel format
@app.route("/download", methods=["GET"])
def exportFile():
    try:
        data = dataExtractor.read_database(mongo)  # Retrieve data from MongoDB
        response = dataExtractor.modifyToExcel(data)  # Modify data and export to Excel
        return response, 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Uncomment the following block to run the app locally
# if __name__ == "__main__":
#     app.run(debug=True, host="0.0.0.0")
