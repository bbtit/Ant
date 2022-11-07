import csv

f = open("./sample.csv", "a", newline = "")

writer = csv.writer(f)

My_list = [
["イチゴ", "40"],
["オレンジ", "200"],
]

for data in My_list:
    writer.writerow(data)
f.close()