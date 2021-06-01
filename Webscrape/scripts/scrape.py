from time import sleep
import requests
from datetime import datetime

global requests_counter
requests_counter = 0

def read_range():
    data = []
    file = open("D:\projects\Pythonnnn\TuluProject\Webscrape\data\ids_ranges.txt", "r")
    for line in file:
        data.append(line)
    return data

def get(id, index, file):
    global requests_counter
    timeouts = 0
    r = None
    while r is None:
        try:
            sleep(1)
            r = requests.get(('https://tuludictionary.in/dictionary/cgi-bin/web/html/detail.php?search=' + str(id) + '00000000' + str(index)), timeout=5)
            #print(repr(r.text))
            requests_counter += 1
            file.write(repr(r.text))
            file.write("\n")
            file.flush()
        except Exception as e:
            print(e)
            now = datetime.now()
            print(" Timed Out :", now.strftime("%H:%M:%S"))
            sleep(5)
            timeouts +=1
            if timeouts == 3:
                requests_counter += 3
                print(id,index)
                return index
    return None

def save_pointer(val, current_id, file):
    if val is not None:
        f = open('D:/projects/Pythonnnn/TuluProject/Webscrape/data/pointer.txt', 'w')
        f.write(str(current_id)+'\n')
        f.write(str(val)+'\n')
        f.close()
        f1 = open('D:/projects/Pythonnnn/TuluProject/Webscrape/data/requests.txt', 'a')
        f1.write(str(requests_counter)+'\n')
        f1.close()
        file.close()
        exit()

def check(d,pos,file):
    data = d[pos].split(' : ')
    file.write(data[0]+'\n')
    for i in range(1, int(data[1]) + 1):
        save_pointer(get(int(data[0]), i, file), pos, file)
    file.write('\n')
    file.flush()

def check_init(d,pos,file,index):
    data = d[pos].split(' : ')
    for i in range(index, int(data[1]) + 1):
        save_pointer(get(int(data[0]), i, file), pos, file)
    file.write('\n')
    file.flush()


d = read_range()

f1 = open('D:/projects/Pythonnnn/TuluProject/Webscrape/data/raw_html_data.txt','a',encoding="utf-8")
f2 = open('D:/projects/Pythonnnn/TuluProject/Webscrape/data/pointer.txt','r')

pos = int(f2.readline())
index = int(f2.readline())

f2.close()

check_init(d,pos,f1,index)

pos += 1

for i in range(pos,len(d)):
    print(i)
    sleep(1)
    check(d,i,f1)





