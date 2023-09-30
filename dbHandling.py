from pymongo import UpdateOne
from pymongo.errors import PyMongoError


def add_to_database(mongo, array_of_dictionaries):
    try:
        selected_document = array_of_dictionaries[0]["name"]
        collection = mongo.db.anemiaData
        # bulk_inserts = []
        bulk_updates = []

        document = collection.find_one({"state": selected_document})

        if document:
            # update_operations = {"$push": {}}
            data = document.get("data", [])
            for item in array_of_dictionaries:
                matching_object = next(
                    (obj for obj in data if obj.get("name") == item["name"]), None
                )
                if matching_object:
                    for key, value in item.items():
                        if key != "name":
                            matching_object.setdefault(key, [])
                            matching_object[key].append(value)
                else:
                    data.append(item)
            collection.update_one(
                {"state": selected_document},
                {"$set": {"data": data}},
            )
        else:
            new_document = {"state": selected_document, "data": []}

            for item in array_of_dictionaries:
                new_item = {"name": item["name"]}
                for key, value in item.items():
                    if key != "name":
                        new_item[key] = [value]
                new_document["data"].append(new_item)
            bulk_updates.append(
                UpdateOne(
                    {"state": selected_document}, {"$set": new_document}, upsert=True
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


# def add_to_database(mongo, array_of_dictionaries):
#     try:
#         which_collection = array_of_dictionaries[0]["name"]
#         collection = mongo.db.anemiaData
#         bulk_inserts = []
#         bulk_updates = []
#         for item in array_of_dictionaries:
#             document = collection.find_one({"name": item["name"]})
#             if document:
#                 update_operations = []
#                 for key, value in item.items():
#                     if key != "name":
#                         update_operations.append(
#                             UpdateOne({"name": item["name"]}, {"$push": {key: value}})
#                         )
#                 bulk_updates.extend(update_operations)
#             else:
#                 new_document = {}
#                 for key, value in item.items():
#                     if key == "name":
#                         new_document[key] = value
#                     else:
#                         new_document[key] = [value]
#                 bulk_inserts.append(new_document)
#         if bulk_inserts:
#             collection.insert_many(bulk_inserts)
#         if bulk_updates:
#             collection.bulk_write(bulk_updates)
#         if bulk_inserts or bulk_updates:
#             return {"status": "SUCCESS"}
#         else:
#             return {"status": "No data to insert or update"}
#     except PyMongoError as e:
#         print(f"MongoDB Error: {str(e)}")
#         return {"status": "MongoDB Error"}
#     except Exception as e:
#         raise Exception(f"Error processing the file: {str(e)}")


def read_database(mongo):
    try:
        collection = mongo.db.anemiaData
        documents = list(collection.find({}, {"_id": 0}))
        return documents
    except Exception as e:
        raise Exception(f"Error processing the file: {str(e)}")
