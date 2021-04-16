import concurrent.futures
from datetime import datetime

import requests
import bs4
import time

now = datetime.now()
start = now.strftime("%H:%M:%S")
print("start Time =", start)

ids = [*range(1,6001)]

def check_id(id):
    try:
        soup = bs4.BeautifulSoup(requests.get('https://tuludictionary.in/dictionary/cgi-bin/web/html/detail.php?search=' + str(id) + '000000001').content, 'html.parser')
        string = str.replace(str.replace(soup.b.__str__(), '\n', ''), ' ', '')
        if string == '<b>  </b>':
            return None
        else:
            return id
    except:
        time.sleep(5)
        check_id(id)


with concurrent.futures.ThreadPoolExecutor() as executor:
    results = executor.map(check_id, ids)

    f = open("../data/ids.txt", "w")
    for id in results:
        if id is not None:
            f.write(str(id)+'\n')

now = datetime.now()
end = now.strftime("%H:%M:%S")
print("end Time =", end)



