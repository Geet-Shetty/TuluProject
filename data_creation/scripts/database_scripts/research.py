from bs4 import BeautifulSoup

raw_html_data = open('D:\projects\Pythonnnn\TuluProject\data_creation\data\\raw_html_data.txt', 'r', encoding="utf-8")

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

# headers_dict = create_headers_dict(raw_html_data)
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

write_as_html_files(
    find_and_list(raw_html_data,"MEANINGS", 10)
)
