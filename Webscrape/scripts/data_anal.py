import time
from datetime import datetime

import bs4
import requests
from requests import ConnectTimeout

ids_n = []

file = open("D:\projects\Pythonnnn\TuluProject\Webscrape\data\ids_ranges.txt", "r")
for line in file:
    ids_n.append(int(line.split(" : ")[1]))


def mean(data):
    sum = 0
    for num in data:
        sum += num

    return sum / len(data)

def median(data):
    data = sorted(data)
    return data[len(data)//2]

print(mean(ids_n))
print(median(ids_n))

def check_id(id,index):
    r = None
    while r is None:
        try:
            r = requests.get(('https://tuludictionary.in/dictionary/cgi-bin/web/html/detail.php?search=' + str(id) + '00000000' + str(index)),timeout=5)
        except:
            now = datetime.now()
            print(" Timed Out :", now.strftime("%H:%M:%S"))
            time.sleep(5)

    if r.text.find("<b>&nbsp") != -1:
        r.close()
        return None
    else:
        r.close()
        return id


print(check_id(1,280))

now = datetime.now()
print("start Time =", now.strftime("%H:%M:%S"))
time.sleep(5)
now = datetime.now()
print("end Time =", now.strftime("%H:%M:%S"))



