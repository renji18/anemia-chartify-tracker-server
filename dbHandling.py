from pymongo import UpdateOne
from pymongo.errors import PyMongoError


def increment_roman_numeral(roman_numeral):
    """
    Increment a Roman numeral (I, II, III, IV).

    Args:
        roman_numeral (str): The Roman numeral to increment.

    Returns:
        str: The incremented Roman numeral.
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
    if type == "quarterly":
        to_quarterly(mongo, array_of_dictionaries)
    elif type == "monthly":
        to_monthly(mongo, array_of_dictionaries)
    else:
        raise ValueError("Invalid type recieved")


def to_monthly(mongo, array_of_dictionaries):
    pass


def to_quarterly(mongo, array_of_dictionaries):
    """
    Add data to the database.

    Args:
        mongo: PyMongo database instance.
        array_of_dictionaries (list): List of dictionaries to add to the database.

    Returns:
        dict: A status message.
    """
    try:
        selected_document = array_of_dictionaries[0]["District"]
        collection = mongo.db.anemiaData
        bulk_updates = []

        document = collection.find_one({"state": selected_document})

        if document:
            data = document.get("data", [])
            quarters = document.get("quarters", [])
        else:
            data = []
            quarters = []

        for item in array_of_dictionaries:
            matching_object = next(
                (obj for obj in data if obj.get("District") == item["District"]), None
            )
            if matching_object:
                for (
                    key,
                    value,
                ) in item.items():
                    if key != "District":
                        matching_object.setdefault(key, [])
                        matching_object[key].append(value)
            else:
                new_item = {"District": item["District"]}
                for key, value in item.items():
                    if key != "District":
                        new_item[key] = [value]
                data.append(new_item)

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

        update_document = {
            "state": selected_document,
            "data": data,
            "quarters": quarters,
        }

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


def read_database(mongo):
    """
    Read data from the database.

    Args:
        mongo: PyMongo database instance.

    Returns:
        list: A list of documents retrieved from the database.
    """
    try:
        collection = mongo.db.anemiaData
        documents = list(collection.find({}, {"_id": 0}))
        return documents
    except Exception as e:
        raise Exception(f"Error processing the file: {str(e)}")


def register_user(mongo, bcrypt, userData):
    """
    Register a user in the database.

    Args:
        mongo: PyMongo database instance.
        bcrypt: Bcrypt instance for password hashing.
        userData (dict): User registration data.

    Returns:
        str: A status message.
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
    Log in a user.

    Args:
        mongo: PyMongo database instance.
        bcrypt: Bcrypt instance for password hashing.
        userData (dict): User login data.

    Returns:
        str: A status message.
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
