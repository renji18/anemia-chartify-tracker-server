
# Anemia Data Processing and Management System

The Anemia Data Processing and Management System is a Python Flask-based web application designed to handle the processing, storage, and retrieval of anemia-related data. It provides functionality for uploading CSV files, processing them, and storing the data in a MongoDB database. Additionally, it supports user registration and login for secure access to the system.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Dependencies](#dependencies)
## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.6 or higher installed on your system.
- MongoDB database available with a connection URI. You can use [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) for cloud-based MongoDB hosting.
- Install required Python packages by running `pip install -r requirements.txt`.
## Installation

Follow these steps to install and set up the project:


1. Clone the repository:

   ```bash
   git clone [https://github.com/your-username/your-project.git](https://github.com/renji18/anemia-chartify-tracker-server/tree/feature-monthly)
   cd your-project

2. Set up a virtual environment (optional but recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate

3. Configure the environment variables by creating a .env file and adding your MongoDB URI:

    ```bash
    MONGO_URI=mongodb+srv://<username>:<password>@cluster0.n5yfn7s.mongodb.net/anemiaDatabase?retryWrites=true&w=majority

4. Start the Flask application:

    ```bash
    python app.py


## Configuration

You can configure the application by modifying the .env file to change the MongoDB connection URI or by adjusting the Flask application configuration in app.py.

## Usage

### Uploading Data
1. Access the system by navigating to http://localhost:5000 in your web browser.

2. Use the provided user registration and login functionality to create an account or sign in.

3. Use the "Upload Data" section to upload CSV files containing anemia-related data. You must specify the data type (either "quarterly" or "monthly") when uploading.

### Retrieving Data
1. Access the system and log in if necessary.

2. Use the "Retrieve Data" section to retrieve anemia-related data. You can specify the data type as a query parameter, e.g., http://localhost:5000/?type=quarterly.


## Dependencies
The project relies on the following Python packages:

```Flask```
```flask-pymongo```
```Flask-CORS```
```python-dotenv```
```pandas```
```Gunicorn```
```flask-bcrypt```

You can install these dependencies using pip install -r requirements.txt.
