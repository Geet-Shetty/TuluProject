import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import time
import concurrent.futures
from bs4 import BeautifulSoup
from io import open
from selenium.common.exceptions import NoSuchWindowException, NoSuchElementException
from datetime import datetime

def grab(tag):
    url = 'https://tuludictionary.in/dictionary/cgi-bin/web/frame.html'

    options = Options()
    options.headless = True

    driver = webdriver.Chrome(r'D:\programs\webstuff\chromedriver.exe', options=options)
    driver.get(url)
    driver.switch_to.frame("search")

    driver.find_element_by_xpath("/html/body/table/tbody/tr/td[1]/form/input[@value='Tulu']").click()
    driver.find_element_by_xpath("/html/body/table/tbody/tr/td[1]/form/input[4]").click()
    driver.find_element_by_xpath("/html/body/table/tbody/tr/td[2]/input[1]").send_keys(tag)
    driver.find_element_by_xpath("/html/body/table/tbody/tr/td[2]/input[2]").click()

    driver.switch_to.default_content()
    driver.switch_to.frame('resultside')

    links = driver.find_elements_by_tag_name("a")

    result = ""
    for link in links:
        driver.switch_to.default_content()
        driver.switch_to.frame('resultside')
        link.click()
        link_t = link.text

        driver.switch_to.default_content()
        driver.switch_to.frame('result')

        html = driver.page_source
        h_soup = BeautifulSoup(html,'html.parser')
        # print(h_soup.prettify())
        # print()
        s = h_soup.get_text(separator="~")

        caps = re.findall(r"([A-Z]+\s?[A-Z]+[^a-z0-9\W])",s)

        m = s.find("MEANINGS")
        try:
            v = s.find(caps[1])
        except IndexError:
            v = s.find('Language References')

        result += link_t + "~" + s[m + 9:v-3] + '\n'

    driver.quit()
    return result

now = datetime.now()

start = now.strftime("%H:%M:%S")
print("start Time =", start)

url = 'https://tuludictionary.in/dictionary/cgi-bin/web/frame.html'

start_time = time.process_time()

options = Options()
options.headless = True

driver = webdriver.Chrome(r'D:\programs\webstuff\chromedriver.exe',options=options)
driver.get(url)
driver.switch_to.frame("search")

driver.find_element_by_xpath("/html/body/table/tbody/tr/td[1]/form/input[@value='English']").click()
driver.find_element_by_xpath("/html/body/table/tbody/tr/td[1]/form/input[6]").click()
driver.find_element_by_xpath("/html/body/table/tbody/tr/td[2]/input[1]").send_keys("monkey")
driver.find_element_by_xpath("/html/body/table/tbody/tr/td[2]/input[2]").click()

driver.implicitly_wait(3)

driver.switch_to.default_content()
driver.switch_to.frame('resultside')

t = None # search results list
while t is None:
    try:
        t = driver.find_element_by_tag_name("td").text
    except (NoSuchWindowException,NoSuchElementException):
        driver.implicitly_wait(1)
        t = driver.find_element_by_tag_name("td").text
        continue

data = t.split("\n")

# data = []
# tags = []
# for tag in tags:
#     data.append(tag.text)

# def grab(tag):
#     tag = tag[tag.find(' ')+1:]
#     tag = tag.replace('ϵ','e')
#     tag = tag.replace('-','')
#     url = 'https://tuludictionary.in/dictionary/cgi-bin/web/frame.html'
#
#     driver = webdriver.Chrome(r'D:\programs\webstuff\chromedriver.exe')
#     driver.get(url)
#     driver.switch_to.frame("search")
#
#     driver.find_element_by_xpath("/html/body/table/tbody/tr/td[1]/form/input[@value='Tulu']").click()
#     driver.find_element_by_xpath("/html/body/table/tbody/tr/td[1]/form/input[4]").click()
#     driver.find_element_by_xpath("/html/body/table/tbody/tr/td[2]/input[1]").send_keys(tag)
#     driver.find_element_by_xpath("/html/body/table/tbody/tr/td[2]/input[2]").click()
#
#     driver.switch_to.default_content()
#     driver.switch_to.frame('resultside')
#
#     link = driver.find_element_by_tag_name("a")
#     link_t = link.text
#     link.click()
#
#     driver.switch_to.default_content()
#     driver.switch_to.frame('result')
#
#     html = driver.page_source
#     h_soup = BeautifulSoup(html,'html.parser')
#     s = h_soup.get_text(separator="~")
#     m = s.find("MEANINGS")
#     v = s.find("VARIATIONS")
#     driver.quit()
#     return link_t + "~" + s[m + 9:v - 3]

if data[0] != 'No results found':
    filtered = []
    for word in data:
        if word[0].isdigit() and word[0] != '1':
            continue
        else:
            if word[0].isdigit():
                word = word[word.find(' ')+1:]
                word = word[word.find(' ')+1:]
            else:
                word = word[word.find(' ')+1:]
            word = word.replace('ϵ', 'e')
            word = word.replace('-', '')
            filtered.append(word)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(grab, filtered)

        lines = []
        for result in results:
            lines.append(result.__str__())

        with open(os.path.join('D:\projects\Pythonnnn\TuluProject\Webscrape\data\outputs', 'text.txt'), "w", encoding="utf-8") as f:
            for line in lines:
                f.write(line)


driver.quit()

now = datetime.now()
end = now.strftime("%H:%M:%S")
print("end Time =", end)