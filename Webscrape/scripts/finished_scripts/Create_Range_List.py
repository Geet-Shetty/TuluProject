import concurrent.futures
from datetime import datetime
import time
import requests
import bs4

ids = []

file = open("/Webscrape/data/ids.txt", "r")
for line in file:
    ids.append(int(line))

def check_id(id,index):
    timeout = 0
    time.sleep(2)
    r = None
    while r is None:
        try:
            r = requests.get(('https://tuludictionary.in/dictionary/cgi-bin/web/html/detail.php?search=' + str(id) + '00000000' + str(index)),timeout=5)
        except:
            timeout += 1
            now = datetime.now()
            print(" Timed Out :", now.strftime("%H:%M:%S"))
            if timeout == 3:
                time.sleep(20)
                print("Strike Out")
                timeout = 0
            time.sleep(5)

    if r.text.find("<b>&nbsp") != -1:
        r.close()
        return None
    else:
        r.close()
        return id

def find_end(id):
    time.sleep(2)
    index = 10
    end = check_id(id, index)
    while end is not None:
        index += 10
        end = check_id(id, index)

    while end is None:
        index -= 1
        end = check_id(id, index)

    return index

def thread_p(data):
    # with concurrent.futures.ThreadPoolExecutor() as executor:
    # results = executor.map(find_end, data)

    results = []
    for id in data:
        results.append(find_end(id))

    f = open("../../data/ids_ranges.txt", "a")
    for index,id in zip(results,data):
        f.write(str(id) + ' : ' + str(index) + '\n')
        f.flush()
    f.close()

start = 1320
end = 1340

while start < len(ids):
    now = datetime.now()
    print("start Time =", now.strftime("%H:%M:%S"))

    print(start,end)
    data = ids[start:end]
    thread_p(data)
    start += 20
    end += 20

    now = datetime.now()
    print("end Time =", now.strftime("%H:%M:%S"))

print(start)

data = ids[1336:]
thread_p(data)
