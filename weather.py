# coding: utf-8

import csv
import datetime
from sys import argv
from urllib.request import urlopen
from bs4 import BeautifulSoup


def import_header_hourly(place_num, now):
    url = urlopen('http://www.data.jma.go.jp/obd/stats/etrn/view/hourly_a1.php?prec_no=' + place_num[0] + \
                  '&block_no=' + place_num[1] + '&year=' + str(now.year) + '&month=' + str(now.month) + \
                  '&day=' + str(now.day) + '&view=p1')
    bsobj = BeautifulSoup(url, "html.parser")

    # テーブルを指定
    table = bsobj.findAll("table", {"class": "data2_s"})[0]
    rows = table.findAll("tr")

    _row = [0] * 2
    tmp = rows[0].findAll(colspan="2")
    _row[0] = [i.get_text() for i in tmp]
    tmp = rows[1].findAll('th')
    _row[1] = [i.get_text() for i in tmp]

    row = rows[0].findAll('th')
    row = [i.get_text() for i in row]

    header = ['日', '時間']
    x = 1
    m = 0
    while x < len(row):
        if _row[0][m] == row[x]:
            tmp = row[x] + ' ' + _row[1][m*2]
            header.append(tmp)
            tmp = row[x] + ' ' + _row[1][m*2+1]
            header.append(tmp)
            m += 1
        else:
            header.append(row[x])
        x += 1

    return header


def import_header_daily(place_num, now):
    url = urlopen('http://www.data.jma.go.jp/obd/stats/etrn/view/daily_a1.php?prec_no=' + place_num[0] + \
                  '&block_no=' + place_num[1] + '&year=' + str(now.year) + '&month=' + str(now.month) + \
                  '&day=' + str(now.day) + '&view=p1')
    bsobj = BeautifulSoup(url, "html.parser")

    # テーブルを指定
    table = bsobj.findAll("table", {"class": "data2_s"})[0]
    rows = table.findAll("tr")

    _row = [0] * 2
    tmp = rows[0].findAll(colspan="2")
    _row[0] = [i.get_text() for i in tmp]
    tmp = rows[1].findAll('th')
    _row[1] = [i.get_text() for i in tmp]

    row = rows[0].findAll('th')
    row = [i.get_text() for i in row]

    header = ['日', '時間']
    x = 1
    m = 0
    while x < len(row):
        if _row[0][m] == row[x]:
            tmp = row[x] + ' ' + _row[1][m*2]
            header.append(tmp)
            tmp = row[x] + ' ' + _row[1][m*2+1]
            header.append(tmp)
            m += 1
        else:
            header.append(row[x])
        x += 1

    return header


def import_data_hourly(place_num, start, end):
    tmp = []
    x = 0
    now = start
    while now <= end:
        print(now)
        url = urlopen('http://www.data.jma.go.jp/obd/stats/etrn/view/hourly_a1.php?prec_no=' + place_num[0] + \
                      '&block_no=' + place_num[1] + '&year=' + str(now.year) + '&month=' + str(now.month) + \
                      '&day=' + str(now.day) + '&view=p1')
        bsobj = BeautifulSoup(url, "html.parser")

        # テーブルを指定
        table = bsobj.findAll("table", {"class": "data2_s"})[0]
        rows = table.findAll("tr")

        for row in rows:
            get_data = row.findAll(['td'])
            if get_data:
                tmp.append([])
                tmp[x].append(now.strftime('%Y-%m-%d'))
                tmp[x].append('{0:02d}'.format(int(get_data[0].text) - 1) + ':00')
                # tmp[x].append((get_data[0].text-1).zfill(2) + ':00')
                for text in get_data[1:]:
                    tmp[x].append(text.get_text())
                x += 1
        now += datetime.timedelta(days=1)

    return tmp


def import_data_daily(place_num, start, end):
    tmp = []
    x = 0
    now = start
    while now <= end:
        print(now)
        url = urlopen('http://www.data.jma.go.jp/obd/stats/etrn/view/daily_a1.php?prec_no=' + place_num[0] + \
                      '&block_no=' + place_num[1] + '&year=' + str(now.year) + '&month=' + str(now.month) + \
                      '&day=' + str(now.day) + '&view=p1')
        bsobj = BeautifulSoup(url, "html.parser")

        # テーブルを指定
        table = bsobj.findAll("table", {"class": "data2_s"})[0]
        rows = table.findAll("tr")

        for row in rows:
            get_data = row.findAll(['td'])
            if get_data:
                tmp.append([])
                tmp[x].append(now.strftime('%Y-%m') + '-' + str(int(get_data[0].text)))
                tmp[x].append('00:00')
                for text in get_data[1:]:
                    tmp[x].append(text.get_text())
                x += 1
        if now.month == 12:
            a = 1
        else:
            a = now.month + 1
        while now.month != a:
            now += datetime.timedelta(days=1)

    return tmp


def main():
    # 使用する地点とスクレイピング用データ
    place = {
        'Namie': ['36', '0295']
    }

    start = datetime.datetime.strptime(argv[1], '%Y/%m/%d')
    end = datetime.datetime.strptime(argv[2], '%Y/%m/%d')
    print(start, end)

    # header = import_header_hourly(place['Namie'], start)
    # data = import_data_hourly(place['Namie'], start, end)
    data = import_data_daily(place['Namie'], start, end)

    with open('test_weather.csv', 'w') as f:
        writer = csv.writer(f, lineterminator='\n')  # 改行コード(\n)
        # writer.writerow(header)
        writer.writerows(data)
    print('Output test_weather.csv')

if __name__ == '__main__':
    main()
