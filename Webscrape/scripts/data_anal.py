ids_n = []

file = open("D:\projects\Pythonnnn\TuluProject\Webscrape\data\ids_ranges.txt", "r")
for line in file:
    ids_n.append(int(line.split(" : ")[1]))

# 29 2 and ended at 119 23

def count(s_id, s_index, e_id, e_index, data):
    data = data[s_id:e_id+1]
    sum = 0
    for val in data:
        sum += val
    sum -= (s_index + data[len(data)-1] - e_index - 1)
    print(sum)

def mean(data):
    sum = 0
    for num in data:
        sum += num

    print("total:",sum)
    return sum / len(data)

def median(data):
    data = sorted(data)
    return data[len(data)//2]

def map_count(num):
    step = 10
    remainder = num % step
    total = (num - remainder)/step
    if(remainder != 0):
          total += (step-remainder)
    return total

def find_min_requests(data):
    sum = 0
    for max in data:
        sum += map_count(max)
    return sum

# print(find_min_requests(ids_n))
# print(mean(ids_n))
# print(median(ids_n))

# count(29,2,119,23,ids_n)

def file_len(fname):
    c = 0
    with open(fname,encoding="utf-8") as f:
        for i, l in enumerate(f):
            if 'html' in l:
                c += 1
    return c

print( round((file_len('D:\projects\Pythonnnn\TuluProject\Webscrape\data\\raw_html_data.txt')/68495) * 100,2), '%')
