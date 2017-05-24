# coding: utf-8

import argparse
import datetime
import csv
import os
import os.path
import numpy as np
import matplotlib.pyplot as plt


def load_inet_data(fname):
    """
    Input data format
    fname: csv filename

    Return data format
    {'datetime': datetime.datetime(), 'id1': (sensor1 data), 'id2': (sensor2 data)}
    """
    f = open(fname, 'r')
    d = csv.reader(f)
    i_data = []
    for i in d:
        append = str(i[0]) + '/' + str(i[1])
        t = {'datetime': datetime.datetime.strptime(append, '%Y-%m-%d/%H:%M'),
             'id1': i[2],
             'id2': i[3]}
        i_data.append(t)

    return i_data


def type_split(a, b):
    """
    Input data format
    sensor data1, sensor data2 

    Return data
    'xx' or 'ox' or 'xo' or 'oo' or '.'
    """

    if a == 'x' or b == 'x' or a == 'X' or b == 'X':
        return '.'

    # 10進数変換
    a = int(a, 16)
    b = int(b, 16)

    if a == 0 and b == 0:  # xx
        return 'xx'
    elif a != 0 and b == 0:  # ox
        return 'ox'
    elif a == 0 and b != 0:  # xo
        return 'xo'
    else:  # oo
        return 'oo'


def reshape_data(data, interval='1hour'):
    """
    Input data format
    2000-01-01,00:00,0,0 (date, id1, id2)

    Return data format
    {'data': sum, 'status': _frame} (_frame: 'x','o')
    """

    if interval == '1hour':
        skip = 3600
    else:
        skip = 1800

    flag = False
    _flag = False
    _data = []
    x = -1
    dsum = 0
    now = data[0]['datetime'] + datetime.timedelta(days=-1)

    for day in data:

        difference = day['datetime'] - now
        if difference.days == 1:
            if day['datetime'] != data[0]['datetime']:
                _data[x].append({'status': 'o' if flag else 'x', 'data': dsum})

            x += 1
            dsum = 1
            _data.append([])
            now = day['datetime']
            flag = False
        elif difference.seconds % skip == 0:
            if flag and flag != _flag:
                _data[x].append({'status': 'x', 'data': dsum - 1})
                dsum = 1
                _flag = True
            elif not flag and flag != _flag:
                _data[x].append({'status': 'o', 'data': dsum - 1})
                dsum = 1
                _flag = False
            flag = False
            dsum += 1

        if type_split(day['id1'], day['id2']) == 'xo' or type_split(day['id1'], day['id2']) == 'oo':
            flag = True

    _data[x].append({'status': 'o' if flag else 'x', 'data': dsum})

    return _data


def figuer_plot_activity(fname, data, interval='1hour'):
    """
    Input data format
    load_inet_data() return format (2000-01-01,00:00,0,0 (date, id1, id2))
    """
    name, ext = os.path.splitext(fname)
    if not os.path.exists(name):
        os.mkdir(name)
    _data = reshape_data(data, interval)
    if interval == '1hour':
        skip = 1
    else:
        skip = 2

    # グラフ線画
    a = 0
    while a < len(data):
        now = data[a]['datetime'].month
        days = 0
        while (a + days) < len(data):
            if now != data[a + days]['datetime'].month:
                break
            days += 1440

        new_data = _data[int(a / 1440):int(a + days / 1440)]

        fig, axes = plt.subplots(1, int(days/1440), sharex=True, sharey=True, figsize=(15, 10))

        ind = np.arange(1)
        width = 0.8
        colors = {'x': 'w', 'o': 'g'}
        labels = [i for i in range(1, int(days/1440 + 1))]
        print(labels)

        for i in range(int(days/1440)):
            bottom = 0
            for j in range(len(new_data[i])):
                axes[i].bar(
                    ind,  # バーの左端と重なるx座標
                    new_data[i][j]['data']/skip,  # バーの高さ
                    width,
                    bottom,  # バーが始まる高さ
                    color=colors[new_data[i][j]['status']],  # 色
                    tick_label='',
                    align='center'
                    )
                bottom += new_data[i][j]['data']/skip

        for i in range(len(axes)):
            axes[i].set_xticks(ind + width / 2)
            axes[i].set_xticklabels((str(labels[i]),))

        # plt.show()

        # Print title
        axes[int(days / (1440 * 2))].set_title(str(data[a]['datetime'].year) + '-' + str(data[a]['datetime'].month))
        axes[0].set_ylabel('hour')
        plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0, hspace=0)
        plt.text(1.7, 23.5, 'id2', size=17, weight='bold', ha='left', color='g')
        plt.savefig(str(name) + '/' + 'coarse_' + str(data[a]['datetime'].year) + \
                    '-' + str(data[a]['datetime'].month) + '.png')
        print('coarse_' + str(data[a]['datetime'].year) + '-' + str(data[a]['datetime'].month) + '.png')
        # plt.show()
        plt.close(fig)
        a += days


def main():
    # 引数からファイル名を取得
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv_file")
    parser.add_argument("--encoding", default="utf_8")
    options = parser.parse_args()
    print(options.input_csv_file)
    fname = options.input_csv_file

    i_data = load_inet_data(fname)
    figuer_plot_activity(fname, i_data)

if __name__ == '__main__':
    main()
