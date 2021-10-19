import json
import parse
import pymongo

# Data to be written
# dictionary = {
#     "id": "04",
#     "name": "sunil",
#     "department": "HR"
# }

dictionary = parse.words


with open("research_data/words.txt", "w") as outfile:
    # json.dump(dictionary, outfile)
    for word in dictionary:
        outfile.write(json.dumps(word)+'\n')
# # Serializing json
json_object = json.dumps(dictionary[0])
print(json_object)