import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import time
import concurrent.futures
from bs4 import BeautifulSoup
import io
from selenium.common.exceptions import NoSuchWindowException, NoSuchElementException, NoSuchFrameException
from datetime import datetime

def read(path):
    list = []
    f = open(path,"r")
    for line in f:
        list.append(line.replace('\n',''))
    return list

def read_words(path):
    list = set()
    f = open(path,'r')
    for line in f:
        string = line.replace('\n','')
        if re.search(r"(^[A-Za-z]+$)", string) is not None:
            list.add(string)
    return list

def write_set(set):
    with io.open(os.path.join('D:\projects\Pythonnnn\TuluProject\Webscrape\data\inputs', 'words_filtered.txt'), "w") as f:
        for val in set:
            f.write(val+'\n')

def found(word):
    url = 'https://tuludictionary.in/dictionary/cgi-bin/web/frame.html'

    options = Options()
    options.headless = True

    driver = webdriver.Chrome(r'D:\programs\webstuff\chromedriver.exe', options=options)
    driver.get(url)
    driver.switch_to.frame("search")

    driver.find_element_by_xpath("/html/body/table/tbody/tr/td[1]/form/input[@value='English']").click()
    driver.find_element_by_xpath("/html/body/table/tbody/tr/td[1]/form/input[6]").click()
    driver.find_element_by_xpath("/html/body/table/tbody/tr/td[2]/input[1]").send_keys(word)
    driver.find_element_by_xpath("/html/body/table/tbody/tr/td[2]/input[2]").click()

    driver.implicitly_wait(3)

    driver.switch_to.default_content()
    driver.switch_to.frame('resultside')

    t = None  # search results list
    while t is None:
        try:
            t = driver.find_element_by_tag_name("td").text
        except (NoSuchWindowException, NoSuchElementException):
            driver.implicitly_wait(1)
            t = driver.find_element_by_tag_name("td").text
            continue

    data = t.split("\n")
    driver.quit()
    if data[0] == 'No results found':
        return None
    else:
        return word

now = datetime.now()
start = now.strftime("%H:%M:%S")
print("start Time =", start)

words = read("D:\projects\Pythonnnn\TuluProject\Webscrape\data\inputs\\test_input.txt")

with concurrent.futures.ThreadPoolExecutor() as executor:
    results = executor.map(found, words)

    lines = []
    for result in results:
        if result is not None:
            lines.append(result)

    with io.open(os.path.join('D:\projects\Pythonnnn\TuluProject\Webscrape\data\outputs','test_output.txt'), "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line+'\n')

# data = read_words("D:\projects\Pythonnnn\TuluProject\Webscrape\data\inputs\\words.txt")
# write_set(data)

now = datetime.now()
end = now.strftime("%H:%M:%S")
print("end Time =", end)