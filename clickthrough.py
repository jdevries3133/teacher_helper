import csv 

with open('responses.csv', 'r') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)

    names = []
    for row in reader:
        name = row[2] + ' ' + row[3]
        names.append(name)

with open('out.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    for name in names:
        writer.writerow([name])
