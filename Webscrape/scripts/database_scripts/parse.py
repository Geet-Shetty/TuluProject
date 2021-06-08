from bs4 import BeautifulSoup

raw_html_data = open('/Webscrape/data/raw_html_data.txt', 'r', encoding="utf-8")

bold_tag = ['variations (region/caste wise)', 'dialects', 'suffix', 'meanings', 'examples', 'references', 'language references']

keys = set()

def contains_tag(tag_text):
    tag_text = tag_text.lower();
    for tag in bold_tag:
        if tag_text.__contains__(tag):
            return True
    return False

# for line in raw_html_data:
#     print(line)
#     html_string = raw_html_data.readline()
#     if(html_string.__contains__('html')):
#         h_soup = BeautifulSoup(html_string,'html.parser')
#         # print(h_soup.body.prettify())
#         for tag in h_soup.find_all('b'):
#             current_text = tag.get_text();
#             if '\\n' not in current_text:
#                 keys.add(tag.get_text())
#             # if not contains_tag(tag.get_text()):
#             #     print(tag.get_text())
#
# print(keys)

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

headers_dict = create_headers_dict(raw_html_data)
write_to_file("/Webscrape/scripts/headers_data.txt", headers_dict)

