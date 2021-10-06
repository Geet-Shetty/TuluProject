from bs4 import BeautifulSoup
import os
import path

raw_html_data = open(os.path.join(path.data, 'raw_html_data.txt'), 'r', encoding="utf-8")

def map_tag(raw_html_data, tag):
    img_set = {}
    for html_line in raw_html_data:
        html_soup = BeautifulSoup(html_line, 'html.parser')
        table_list = html_soup.findAll('table')
        for table in table_list:
            header_rows = table.findAll('td')
            for row in header_rows:
                imgs = row.findAll(tag)
                for img in imgs:
                    if img_set.__contains__(str(img)):
                        img_set[str(img)] = img_set[str(img)]+1
                    else:
                        img_set[str(img)] = 0
                # if row.has_attr('class') and row['class'][0] == 'tblhead':
                    # print(row.parent.parent)
                    #print('table title', row.text)
    return img_set

img_set = map_tag(raw_html_data, 'img')

words = open(
    f"bug_checks.txt",
    "w",
    encoding="utf-8")

for img in img_set:
    words.write(img + ' : ' + str(img_set[img]) + '\n')

