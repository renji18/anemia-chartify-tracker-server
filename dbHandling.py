from pymongo import UpdateOne
from pymongo.errors import PyMongoError


def add_to_database(mongo, array_of_dictionaries):
    try:
        collection = mongo.db.anemiaData
        bulk_inserts = []
        bulk_updates = []
        for item in array_of_dictionaries:
            document = collection.find_one({"name": item["name"]})
            if document:
                update_operations = []
                for key, value in item.items():
                    if key != "name":
                        update_operations.append(
                            UpdateOne({"name": item["name"]}, {"$push": {key: value}})
                        )
                bulk_updates.extend(update_operations)
            else:
                new_document = {}
                for key, value in item.items():
                    if key == "name":
                        new_document[key] = value
                    else:
                        new_document[key] = [value]
                bulk_inserts.append(new_document)
        if bulk_inserts:
            collection.insert_many(bulk_inserts)
        if bulk_updates:
            collection.bulk_write(bulk_updates)
        if bulk_inserts or bulk_updates:
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
