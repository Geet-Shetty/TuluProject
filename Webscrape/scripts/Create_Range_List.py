import concurrent.futures
from datetime import datetime
import time
import requests
import bs4

now = datetime.now()
start = now.strftime("%H:%M:%S")
print("start Time =", start)

ids = []

file = open("D:\projects\Pythonnnn\TuluProject\Webscrape\data\ids.txt", "r")
for line in file:
    ids.append(int(line))

# ids = [2208,2811,505]

def check_id(id,index):
    try:
        soup = bs4.BeautifulSoup(requests.get('https://tuludictionary.in/dictionary/cgi-bin/web/html/detail.php?search=' + str(id) + '00000000' + str(index)).content, 'html.parser')
        string = str.replace(str.replace(soup.b.__str__(), '\n', ''), ' ', '')
        if string == '<b>  </b>':
            return None
        else:
            return id
    except:
        time.sleep(5)
        check_id(id)

def find_end(id):
    index = 10
    end = check_id(id, index)
    while end is not None:
        index += 10
        end = check_id(id, index)

    while end is None:
        index -= 1
        end = check_id(id, index)

    return index

# with concurrent.futures.ThreadPoolExecutor() as executor:
#     results = executor.map(find_end, ids)
#
#     f = open("../data/ids_ranges.txt", "w")
#     for index,id in zip(results,ids):
#         f.write(str(id) + ' : ' + str(index) + '\n')


now = datetime.now()
end = now.strftime("%H:%M:%S")
print("end Time =", end)