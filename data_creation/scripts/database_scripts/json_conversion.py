import json
import os
import parse
from data_creation.scripts.database_scripts import path

raw_html_data = open(os.path.join(path.data, 'raw_html_data.txt'),
                     'r',
                     encoding="utf-8")

def create_word_dump():
    # include = open(
    #     f"research_data/word_test.txt",
    #     "w",
    #     encoding="utf-8")
    #
    # exclude = open(
    #     f"word_exclude_m.txt",
    #     "w",
    #     encoding="utf-8")
    data = []
    for html_line in raw_html_data:
        if not html_line.replace("\n","").isdigit() and not html_line == "\n": # don't worry about replace it does not affect the original string
            try:
                word = parse.parse_html(html_line)
                data.append(word)
                # data = f'{word["word"]["kannada"]},{word["word"]["english"]}\n'
                # if not parse.iskannada(word['word']['kannada']) or word["word"]["kannada"] == '' or word["word"]["english"] == '':
                #     exclude.write(html_line)
                # else:
                #     include.write(data)
            except (AttributeError,IndexError):
                print("some error with line: ", html_line)

    return data

dictionary = create_word_dump()

with open("research_data/words.txt", "w") as outfile:
    json.dump(dictionary, outfile)
    # for word in dictionary:
    #     outfile.write(json.dumps(word)+'\n')

# # # Serializing json
# json_object = json.dumps(dictionary[0])
# print(json_object)