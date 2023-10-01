from pymongo import UpdateOne
from pymongo.errors import PyMongoError


def increment_roman_numeral(roman_numeral):
    if roman_numeral == "I":
        return "II"
    elif roman_numeral == "II":
        return "III"
    elif roman_numeral == "III":
        return "IV"
    else:
        raise ValueError("Invalid Roman numeral")


def add_to_database(mongo, array_of_dictionaries):
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
    try:
        collection = mongo.db.anemiaData
        documents = list(collection.find({}, {"_id": 0}))
        return documents
    except Exception as e:
        raise Exception(f"Error processing the file: {str(e)}")
