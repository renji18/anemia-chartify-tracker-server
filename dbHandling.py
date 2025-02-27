from pymongo import UpdateOne
from pymongo.errors import PyMongoError

"""
    The website to convert the pdfs to csvs
    https://products.groupdocs.app/conversion/pdf-to-csv
"""


def increment_roman_numeral(roman_numeral):
    """
    This function takes a Roman numeral as input and increments it by one numeral,
    e.g., "I" to "II," "II" to "III," and "III" to "IV.

    The function uses conditional statements to check the input numeral and increments it accordingly.
    If an invalid numeral is provided, it raises a ValueError with an error message.
    """
    if roman_numeral == "I":
        return "II"
    elif roman_numeral == "II":
        return "III"
    elif roman_numeral == "III":
        return "IV"
    else:
        raise ValueError("Invalid Roman numeral")


def add_to_database(mongo, array_of_dictionaries, type):
    """
    This function adds data to a MongoDB collection based on the provided type parameter.
    It handles both quarterly and monthly data differently.

    The function determines the appropriate MongoDB collection based on the type parameter (either "quarterly" or "monthly").

    It then processes and updates the data in the collection. For quarterly data, it also increments the quarter value (e.g., from "2021_I" to "2021_II").

    The function uses bulk updates for efficiency, and it handles exceptions such as MongoDB errors and invalid type values.
    """
    try:
        # Extracting the state name for MongoDB collection selection
        selected_document = array_of_dictionaries[0]["District"]

        # Selecting the MongoDB collection based on the provided type
        if type == "quarterly":
            collection = mongo.db.anemiaDataQuarterly
        elif type == "monthly":
            collection = mongo.db.anemiaDataMonthly
        else:
            raise ValueError("Invalid type passed")

        # Initializing empty lists and variables
        bulk_updates = []
        document = collection.find_one({"state": selected_document})
        if document:
            data = document.get("data", [])
            if type == "quarterly":
                quarters = document.get("quarters", [])
        else:
            data = []
            if type == "quarterly":
                quarters = []

        # Iterating through the input data and updating the MongoDB collection
        for item in array_of_dictionaries:
            matching_object = next(
                (obj for obj in data if obj.get("District") == item["District"]),
                None,
            )
            if matching_object:
                for (
                    key,
                    value,
                ) in item.items():
                    if key != "District":
                        if type == "quarterly":
                            matching_object.setdefault(key, [])
                            matching_object[key].append(value)
                        elif type == "monthly":
                            if len(matching_object[key][-1]["data"]) < 12:
                                matching_object[key][-1]["data"].append(value)
                            else:
                                last_year = matching_object[key][-1]["year"]
                                new_year = last_year + 1
                                new_obj = {"year": new_year, "data": [value]}
                                matching_object[key].append(new_obj)
                        else:
                            raise ValueError("Invalid type passed")
            else:
                new_item = {"District": item["District"]}
                for key, value in item.items():
                    if key != "District":
                        if type == "quarterly":
                            new_item[key] = [value]
                        elif type == "monthly":
                            new_item[key] = [{"year": 2021, "data": [value]}]
                        else:
                            raise ValueError("Invalid type passed")
                data.append(new_item)

        # Incrementing quarterly data if applicable
        if type == "quarterly":
            if quarters == []:
                quarters.append("2021_I")
            else:
                last_quarter = quarters[-1]
                year, roman_numeral = last_quarter.split("_")
                if roman_numeral == "IV":
                    year = str(int(year) + 1)
                    roman_numeral = "I"
                else:
                    roman_numeral = increment_roman_numeral(roman_numeral)
                quarters.append(f"{year}_{roman_numeral}")

        # Creating the update document for MongoDB
        if type == "quarterly":
            update_document = {
                "state": selected_document,
                "data": data,
                "quarters": quarters,
            }
        elif type == "monthly":
            update_document = {
                "state": selected_document,
                "data": data,
            }
        else:
            raise ValueError("Invalid type passed")

        # Creating the MongoDB update operations
        if document:
            bulk_updates.append(
                UpdateOne({"state": selected_document}, {"$set": update_document})
            )
        else:
            bulk_updates.append(
                UpdateOne(
                    {"state": selected_document}, {"$set": update_document}, upsert=True
                )
            )

        # Performing the bulk write to MongoDB
        if bulk_updates:
            collection.bulk_write(bulk_updates)
            return {"status": "SUCCESS"}
        else:
            return {"status": "No data to insert or update"}
    except PyMongoError as e:
        print(f"MongoDB Error: {str(e)}")
        return {"status": "MongoDB Error"}
    except Exception as e:
        raise Exception(f"Error processing the file: {str(e)}")


def read_database(mongo, type):
    """
    This function retrieves data from a MongoDB collection based on the provided type parameter (either "quarterly" or "monthly").

    The function determines the appropriate MongoDB collection based on the type parameter and retrieves documents from that collection.

    It handles exceptions and raises a ValueError for an invalid type value.
    """
    try:
        if type == "quarterly":
            collection = mongo.db.anemiaDataQuarterly
        elif type == "monthly":
            collection = mongo.db.anemiaDataMonthly
        else:
            raise ValueError("Invalid type passed")
        documents = list(collection.find({}, {"_id": 0}))
        return documents
    except Exception as e:
        raise Exception(f"Error processing the file: {str(e)}")


def register_user(mongo, bcrypt, userData):
    """
    This function registers a new user in a MongoDB collection by hashing the user's password and storing it securely.

    It checks if the provided username already exists in the database.

    If not, it hashes the user's password and inserts the user data into the "userData" collection.
    """
    try:
        collection = mongo.db.userData
        existing_user = collection.find_one({"username": userData["userName"]})
        if existing_user:
            return "Username already exists"
        hashed_password = bcrypt.generate_password_hash(userData["password"]).decode(
            "utf-8"
        )
        new_user = {"username": userData["userName"], "password": hashed_password}
        collection.insert_one(new_user)
        return "success"
    except Exception as e:
        raise Exception(f"Error registering user: {str(e)}")


def login_user(mongo, bcrypt, userData):
    """
    This function handles user login by checking the provided username and password against the stored data in a MongoDB collection.

    It first checks if the provided username exists in the database.
    If the username exists, it compares the hashed password with the provided password using the bcrypt library.
    """
    try:
        collection = mongo.db.userData
        user = collection.find_one({"username": userData["userName"]})
        if user:
            hashed_password = user.get("password", "")
            if bcrypt.check_password_hash(hashed_password, userData["password"]):
                return "User Logged In Successfully"
            else:
                return "Invalid Password"
        else:
            return "User Not Found"
    except Exception as e:
        raise Exception(f"Error registering user: {str(e)}")
