import csv
import os


for i in os.listdir('.'):
    if i[-4:] != '.csv':
        continue
    if i[0] == "~" or i[0] == ".":
        continue
    data = []
    try:
        with open(i, 'r', encoding='utf_8') as csvfile:
            rows = []
            for row in csv.reader(csvfile):
                rows.append(row)
            data += rows
    except (UnicodeDecodeError, IOError):
        continue
    try:
        topic = data[1][1][:9]
        start_time = data[1][2]
        date = start_time.split(' ')[0].replace('/', '-')
    except IndexError:
        raise Exception('jack: Not yet implemented')
    new_name = topic + ' ' + date + '.csv'
    os.rename(i, new_name)
