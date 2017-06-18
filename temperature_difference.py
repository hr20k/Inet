# coding: utf-8

import argparse
import datetime
import csv
import os
import os.path
from sys import argv


def load_weather_csv(fname, area):
    f = open(fname, 'r', encoding='shift-jis')
    d = csv.reader(f)
    data = []
    for i in d:
        link = str(i[0]) + '/' + str(i[1])
        t = {'datetime': datetime.datetime.strptime(link, '%Y-%m-%d/%H:%M'),
             'ta': i[area]}
        data.append(t)
    
    return data


def main():
    # 使用する地点とスクレイピング用データ(area: [hourly, daily])
    place = {
        'Namie': [3, 5],
        'Soma': [3, 5],
        'Hirono': [3, 5],
        'Fukushima': [5, 6],
        'Onahama': [5, 6],
        'Sirakawa': [5, 6],
        'Wakamatsu': [5, 6]
    }
    interval = 'hourly'  # 'hourly' or 'daily'

    # # 引数からファイル名を取得
    # parser = argparse.ArgumentParser()
    # parser.add_argument("input_csv_file")
    # # parser.add_argument("--encoding", default="utf_8")
    # parser.add_argument("--encoding", default="shift_jis")
    # options = parser.parse_args()
    # print(options.input_csv_file)
    # fname = options.input_csv_file

    fname = [argv[1], argv[2]]

    area = []
    for name in fname:
        for i in place:
            if i in name:
                print(i)
                area.append(i)
                if not (interval in name):
                    interval = 'daily'
                break

    print(area, interval)

    if area != '':
        data1 = load_weather_csv(fname[0], place[area[0]][0 if interval == 'hourly' else 1])
        data2 = load_weather_csv(fname[1], place[area[1]][0 if interval == 'hourly' else 1])
        for i in data1:
            print(i)
        for i in data2:
            print(i)
    else:
        print('Wrong data.')


if __name__ == '__main__':
    main()

