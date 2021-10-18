from bs4 import BeautifulSoup
import re
import os
import path
import parse
raw_html_data = open(os.path.join(path.data, 'raw_html_data.txt'), 'r', encoding="utf-8")

bold_tag = ['variations (region/caste wise)', 'dialects', 'suffix', 'meanings', 'examples', 'references', 'language references']

keys = set()

def contains_tag(tag_text):
    tag_text = tag_text.lower();
    for tag in bold_tag:
        if tag_text.__contains__(tag):
            return True
    return False

def create_headers_dict(html_data):
    headers_dict = {}
    for line in html_data:
        if line.__contains__('html'):
            line_html = BeautifulSoup(line,'html.parser')
            for tag in line_html.find_all('b'):
                current_text = tag.get_text();
                if '\\n' not in current_text:
                    if current_text.__contains__('Uses'):
                        print()
                    if headers_dict.__contains__(current_text):
                        headers_dict[current_text] += 1
                    else:
                        headers_dict[current_text] = 0
    return headers_dict

def write_to_file(filepath, dictionary):
    file = open(filepath, "w", encoding="utf-8")
    for header, count in dictionary.items():
        file.write(header + " : " + str(count) + '\n')
    file.close()

#headers_dict = create_headers_dict(raw_html_data)
# write_to_file("/data_creation/scripts/headers_data.txt", headers_dict)

def read_dict(filepath):
    dict = {}
    file = open(filepath, "r", encoding="utf-8")
    for line in file:
        key_value = line.split(" : ")
        dict[key_value[0]] = int(key_value[1])

    return dict

def start_contains(string):
    words = ['Bhagavato.', 'MR.', 'GM.', 'Kv.', 'GT.', 'AM.', 'PV.', 'MG.', 'AS.', 'SK.', 'KP.']
    for word in words:
        if string.startswith(word):
            return word
    return None

def remove_variations(headers_count):
    new_header_count = {}
    for header, count in headers_count.items():
        dup_word = start_contains(header)
        if dup_word is not None:
            if new_header_count.__contains__(dup_word):
                new_header_count[dup_word] += count+1
            else:
                new_header_count[dup_word] = count+1
        else:
            new_header_count[header] = count+1
    return new_header_count

def find_and_prettify(raw_html_data, string):
    for line in raw_html_data:
        if line.__contains__(string):
            line_html = BeautifulSoup(line, 'html.parser')
            print(line_html.prettify())
            return line
    print("Not Found.")

def in_file(file, string):
    for line in file:
        if line == string:
            return True
    return False

def find_and_list(raw_html_data, string, list_len):
    lines = []
    pulled_file = open("D:\projects\Pythonnnn\TuluProject\data_creation\scripts\database_scripts\html_view\pulled.txt", "r", encoding="utf-8")
    for line in raw_html_data:
        if list_len == 0:
            pulled_file.close()
            pulled_file = open("D:\projects\Pythonnnn\TuluProject\data_creation\scripts\database_scripts\html_view\pulled.txt", "a", encoding="utf-8")
            for l in lines:
                pulled_file.write(str(l))
            return lines
        elif line.__contains__(string) and not in_file(pulled_file, line):
            line_html = BeautifulSoup(line, 'html.parser')
            lines.append(line_html)
            print(line_html)
            list_len -= 1

    print("Not Found.")

def write_as_html(string):
    f = open("D:\projects\Pythonnnn\TuluProject\data_creation\scripts\database_scripts\html_view\page.html", "w", encoding="utf-8")
    f.write(string[1:(len(string) - 4)])
    f.close()

def write_as_html_files(strings):
    file_count = len(strings)
    for string in strings:
        f = open(f"D:\projects\Pythonnnn\TuluProject\data_creation\scripts\database_scripts\html_view\page{file_count}.html", "w",
                 encoding="utf-8")
        f.write(str(string))
        file_count -= 1

# header_count = read_dict("D:\projects\Pythonnnn\TuluProject\data_creation\scripts\database_scripts\headers_data.txt")
#
# header_count = remove_variations(header_count)
#
# write_to_file("D:\projects\Pythonnnn\TuluProject\data_creation\scripts\database_scripts\headers_data_sorted.txt",dict(sorted(header_count.items(), key=lambda item: item[1])))

# write_as_html_files(
#     find_and_list(raw_html_data,"MEANINGS", 10)
# )

def find_different(raw_html_file, tags, tag_type):
    new_tags = []
    dup_tags = set()
    for line in raw_html_data:
        line_html = BeautifulSoup(line, 'html.parser')
        line_tags = line_html.find_all(tag_type)
        if len(line_tags) != 0:
            for line_tag in line_tags:
                if line_tag not in dup_tags:
                    for tag in tags:
                        if line_tag != tag:
                            new_tags.append(line)
                    dup_tags.add(line_tag)

    f = open(
        f"research_data/dump.txt",
        "w",
        encoding="utf-8")
    for tag in new_tags:
        f.write(tag)
    f.close()

# tags = ['<img src="images/EBig.JPG"/>']
# find_different(raw_html_data,tags,'img')

# f = open(
#     f"D:\projects\Pythonnnn\TuluProject\data_creation\scripts\database_scripts\dump.txt",
#     "r",
#     encoding="utf-8")
#
# line = find_and_prettify(raw_html_data,"ಅತಿಯುಕ್ತಿ ( ಕುಳು)")
# print("done")

def substring_until(string, start, end_at_char):
    index = start
    while index < len(string):
        if string[index] == end_at_char:
            return string[start:index]
        index += 1

def new_codes(raw_html_data, dump_file):
    # common layout is number + eight zeros + number
    # rare is seven or nine zeros and/or has letter after second number

    codes = []

    # find the javascript codes in html line
    # javascript:cFunc("code")
    for line in raw_html_data:
        indices = [m.start() for m in re.finditer("javascript:cFunc", line)] # learn the regex stuff later lmao
        for index in indices:
            code = substring_until(line,index+(len('javascript:cFunc("')),'"') # index starts at j in javascript:cFunc
            if code.__contains__('00000000'):
                if code[len(code)-1].isalpha():
                    codes.append(code)
            else:
                codes.append(code)

    for code in codes:
        dump_file.write(code+'\n')

    dump_file.close()

# dump = open(
#     f"D:\projects\Pythonnnn\TuluProject\data_creation\scripts\database_scripts\dump2.txt",
#     "w",
#     encoding="utf-8")
#
# new_codes(raw_html_data, dump)

# find_and_prettify('kaṭṭaḷϵ kandaacaara')



def create_word_dump(): # check that imgs don't exist in the meanings context (not the headers)
    include = open(
        f"research_data/word_test.txt",
        "w",
        encoding="utf-8")

    exclude = open(
        f"word_exclude_m.txt",
        "w",
        encoding="utf-8")

    count = 0
    for html_line in raw_html_data:
        if not html_line.replace("\n","").isdigit() and not html_line == "\n":
            count += 1
            try:
                html_soup = BeautifulSoup(html_line, 'html.parser')
                # header = html_soup.findAll('center') # center is only used in word and origin display at the top
                # word_text = header[0].find('b').text

                table_list = html_soup.findAll('table')
                for table in table_list:
                    header_rows = table.findAll('td')
                    for row in header_rows:
                        if row.has_attr('class') and row['class'][0] == 'tblhead':
                            if row.text == 'MEANINGS':
                                tr_elements = row.parent.parent.findAll('tr')
                                tr_elements = tr_elements[1:len(tr_elements)]
                                for tr in tr_elements:
                                    td = tr.find('td')
                                    if td.has_attr('colspan'):
                                       continue
                                    else:
                                        if len(td.findAll('a')) > 0:
                                            exclude.write(html_line)

            except (AttributeError,IndexError):
                print("testsstttt", html_line)

# create_word_dump()

def list(): # check that imgs don't exist in the meanings context (not the headers)
    # exclude = open(
    #     f"research_data\word_exclude_m.txt",
    #     "w",
    #     encoding="utf-8")
    # s = set()
    refs = open(
        f"research_data\\reftexts.txt",
        "w",
        encoding="utf-8")
    count = 0
    for html_line in raw_html_data:
        if not html_line.replace("\n","").isdigit() and not html_line == "\n":
            count += 1
            try:
                html_soup = BeautifulSoup(html_line, 'html.parser')
                table_list = html_soup.findAll('table')
                for table in table_list:
                    header_rows = table.findAll('td')
                    for row in header_rows:
                        if row.has_attr('class') and row['class'][0] == 'tblhead':
                            if row.text == 'REFERENCES':
                                td_elements = table.findAll('td')
                                td_elements = td_elements[
                                              1:len(td_elements)]  # remove first td that is just the title REFERENCES
                                for td in td_elements:
                                    if td.has_attr('colspan'):  # and not td.has_attr('class')
                                       continue
                                    else:
                                        if td.text.isspace():  # if td is empty
                                            continue
                                        text = td.text
                                        refs.write(text + '\n')
                            # if row.text == 'MEANINGS':
                            #     td_elements = table.findAll('td',attrs={"colspan": "3"})
                            #     for td in td_elements:
                            #         test = td.text                                    # list = td.findAll('img')
                            #         # if len(list)>0:
                            #         #     print(html_line)
                            #
                            #         # for references
                            #         # if test.__contains__('Bhagavato'):
                            #         #     continue
                            #         # if len(test) > 3 and test[0].isalpha() and test[1].isalpha() and test[2] == '.':
                            #         #     continue
                            #
                            #         if not s.__contains__(td.text):
                            #             print(test)
                            #         s.add(test)

                            # if row.text == 'EXAMPLES':
                            #     if table.text.count('1.') > 0:
                            #         print(html_line)
                            #     data = ''
                            #     for row in header_rows[1:]:
                            #         if not row.text == '':
                            #             data += row.text + ' newline'
                                # all_text.write(data+'\n')
            except (AttributeError,IndexError):
                print("testsstttt", html_line)

# list()

def sort_file(file_name):
    file = open(
        f"research_data\\{file_name}.txt",
        "r",
        encoding="utf-8")
    out = open(
        f"research_data\\{file_name}_sorted.txt",
        "w",
        encoding="utf-8")
    Lines = file.readlines()
    Lines = sorted(Lines,key=len)
    for line in Lines:
        out.write(line)

# sort_file('reftexts')

def filter(file_name):
    file = open(
        f"research_data\\{file_name}.txt",
        "r",
        encoding="utf-8")
    out = open(
        f"research_data\\{file_name}_filtered.txt",
        "w",
        encoding="utf-8")
    Lines = file.readlines()
    Lines = sorted(Lines,key=len)
    for line in Lines:
        if len(parse.find_occurances(line,' ')) > 3:
            out.write(line)

filter('reftexts_sorted')
# # Using readlines()
# file1 = open(f"research_data/etext.txt", 'r',encoding="utf-8")
# Lines = file1.readlines()
# # Strips the newline character
# for line in Lines:
#     if line.count('newline') > 1:
#         print(line)

# def empty_pages(num):
#     page0 = open(
#         f"D:\projects\Pythonnnn\TuluProject\data_creation\scripts\database_scripts\html_view\page.html",
#         "w",
#         encoding="utf-8")
#
#     page1 = open(
#         f"D:\projects\Pythonnnn\TuluProject\data_creation\scripts\database_scripts\html_view\page1.html",
#         "w",
#         encoding="utf-8")
#
#     count = 0
#     for html_line in raw_html_data:
#         if not html_line.replace("\n","").isdigit() and not html_line == "\n":
#             count += 1
#             try:
#                 if count == num:
#                     page0.write(html_line)
#                     page1.write(raw_html_data.readline())
#                     return
#             except (AttributeError,IndexError):
#                 print("testsstttt", html_line)
#
# # empty_pages(12721) #403, 699, 803,
# #