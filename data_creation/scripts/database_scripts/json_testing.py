import json
import parse

# Data to be written
# dictionary = {
#     "id": "04",
#     "name": "sunil",
#     "department": "HR"
# }

dictionary = [parse.word10,parse.word9]


with open("words.txt", "w") as outfile:
    # json.dump(dictionary, outfile)
    for word in dictionary:
        outfile.write(json.dumps(word)+'\n')
# # Serializing json
json_object = json.dumps(dictionary[0])
print(json_object)