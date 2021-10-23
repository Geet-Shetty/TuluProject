import pymongo
import json
import pymongo as pymongo
from pymongo import MongoClient, InsertOne

from dotenv import load_dotenv
load_dotenv()
import os
print(os.environ.get("CONNECTION"))

client = pymongo.MongoClient(os.environ.get("CONNECTION"))
db = client.dictionary
collection = db.tulus
requesting = []

with open(r"research_data/words.txt") as f:
    for jsonObj in f:
        myDict = json.loads(jsonObj)
        requesting.append(InsertOne(myDict))

result = collection.bulk_write(requesting)
client.close()