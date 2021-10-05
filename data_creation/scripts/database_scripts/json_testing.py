import json
import parse

# Data to be written
# dictionary = {
#     "id": "04",
#     "name": "sunil",
#     "department": "HR"
# }

dictionary = parse.word7

# Serializing json
json_object = json.dumps(dictionary, indent=4)
print(json_object)