def add_to_database(mongo, array_of_dictionaries):
    try:
        collection = mongo.db.anemiaData
        for item in array_of_dictionaries:
            document = collection.find_one({"name": item["name"]})
            if document:
                for key, value in item.items():
                    if key != "name":
                        collection.update_one(
                            {"name": item["name"]}, {"$push": {key: value}}
                        )
            else:
                new_document = {}
                for key, value in item.items():
                    if key == "name":
                        new_document[key] = value
                    else:
                        new_document[key] = [value]
                collection.insert_one(new_document)
        print("SUCCESS")
        return {"status": "SUCCESS"}
    except Exception as e:
        raise Exception(f"Error processing the file: {str(e)}")


def read_database(mongo):
    try:
        collection = mongo.db.anemiaData
        documents = list(collection.find({}, {"_id": 0}))
        return documents
    except Exception as e:
        raise Exception(f"Error processing the file: {str(e)}")
