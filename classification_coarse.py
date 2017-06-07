# coding: utf-8

import argparse
import datetime
import csv
import os
import os.path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import *


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


def type_split(a):
    """
    Input data format
    sensor data

    Return data
    'x' or 'o' or '.'
    """

    if a == 'x' or a == 'X':
        return '.'

    # 10進数変換
    a = int(a, 16)

    if a == 0:  # x
        return 'x'
    else:  # o
        return 'o'


def reshape_data(data, interval='1hour'):
    """
    Input data format
    2000-01-01,00:00,0,0 (date, id1, id2)

    Return data format
    {'data': sum, 'status': _frame} (_frame: 'x', 'o', '.')
    """

    if interval == '1hour':
        skip = 3600
    else:
        skip = 1800

    flag_x = False
    flag_o = False
    _flag = None
    _data = [[]]
    x = 0
    dsum = 0
    now = data[0]['datetime']

    for day in data:

        difference = day['datetime'] - now
        if difference.days == 1:
            print(flag_o, flag_x, _flag)
            if flag_o and _flag != 'o':
                _data[x].append({'status': _flag, 'data': dsum})
                _data[x].append({'status': 'o' if flag_o else 'x' if flag_x else '.', 'data': 1})
            elif flag_x and not flag_o and _flag != 'x':
                _data[x].append({'status': _flag, 'data': dsum})
                _data[x].append({'status': 'o' if flag_o else 'x' if flag_x else '.', 'data': 1})
            elif not flag_o and not flag_x and _flag != '.':
                _data[x].append({'status': _flag, 'data': dsum})
                _data[x].append({'status': 'o' if flag_o else 'x' if flag_x else '.', 'data': 1})
            else:
                _data[x].append({'status': 'o' if flag_o else 'x' if flag_x else '.', 'data': dsum + 1})
            print(_data[x])

            x += 1
            dsum = 0
            _data.append([])
            now = day['datetime']
            flag_o = False
            flag_x = False
            _flag = None

        elif difference.seconds == skip:
            if flag_o:
                _flag = 'o'
            elif flag_x:
                _flag = 'x'
            else:
                _flag = '.'
            dsum += 1
            flag_x = False
            flag_o = False

        elif difference.seconds % skip == 0 and day['datetime'] != data[0]['datetime']:
            print(flag_o, flag_x, _flag)
            if flag_o and _flag != 'o':
                _data[x].append({'status': _flag, 'data': dsum})
                dsum = 1
                _flag = 'o'
            elif flag_x and not flag_o and _flag != 'x':
                _data[x].append({'status': _flag, 'data': dsum})
                dsum = 1
                _flag = 'x'
            elif not flag_o and not flag_x and _flag != '.':
                _data[x].append({'status': _flag, 'data': dsum})
                dsum = 1
                _flag = '.'
            else:
                dsum += 1
            flag_x = False
            flag_o = False

        if type_split(day['id2']) == 'o':
            flag_o = True
            print(day)
        elif type_split(day['id2']) == 'x':
            flag_x = True

    if flag_o and _flag != 'o':
        _data[x].append({'status': _flag, 'data': dsum})
        _data[x].append({'status': 'o' if flag_o else 'x' if flag_x else '.', 'data': 1})
    elif flag_x and not flag_o and _flag != 'x':
        _data[x].append({'status': _flag, 'data': dsum})
        _data[x].append({'status': 'o' if flag_o else 'x' if flag_x else '.', 'data': 1})
    elif not flag_o and not flag_x and _flag != '.':
        _data[x].append({'status': _flag, 'data': dsum})
        _data[x].append({'status': 'o' if flag_o else 'x' if flag_x else '.', 'data': 1})
    else:
        _data[x].append({'status': 'o' if flag_o else 'x' if flag_x else '.', 'data': dsum + 1})
    print(_data[x])

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
        width = 1
        colors = {'x': 'w', 'o': 'g', '.': 'gray'}
        labels = [i for i in range(1, int(days/1440 + 1))]

        for i in range(int(days/1440)):
            bottom = 0

            # select subplot
            plt.subplot(1, int(days/1440), i + 1)

            # Set xticks
            plt.xticks(range(1), (str(labels[i]),))

            # Set yticks
            plt.yticks(np.arange(0, 24, 6))

            # Set axes
            plt.gca().xaxis.set_ticks_position('none')
            if i == 0:
                plt.gca().spines['right'].set_visible(False)
                plt.gca().yaxis.set_ticks_position('left')
            elif i < int(days/1440) - 1:
                plt.gca().spines['right'].set_visible(False)
                plt.gca().yaxis.set_ticks_position('none')
                plt.gca().yaxis.set_ticklabels('')
            else:
                plt.gca().yaxis.set_ticks_position('none')
                plt.gca().yaxis.set_ticklabels('')
            plt.ylim(ymax=24)

            # Set grid
            plt.grid(which='major', axis='y', linestyle='-')
            plt.subplot(1, int(days / 1440), i + 1).yaxis.set_minor_locator(MultipleLocator(3))
            plt.grid(which='minor', axis='y', linestyle='-')

            for j in range(len(new_data[i])):
                plt.bar(
                    ind,  # バーの左端と重なるx座標
                    new_data[i][j]['data']/skip,  # バーの高さ
                    width,
                    bottom,  # バーが始まる高さ
                    color=colors[new_data[i][j]['status']],  # 色
                    align='center'
                )
                bottom += new_data[i][j]['data']/skip

        # Set title
        plt.subplot(1, int(days/1440), int(days / (1440 * 2)))
        plt.title(str(data[a]['datetime'].year) + '-' + str(data[a]['datetime'].month) + ' (id2)', size=22)

        # Set ylabel
        plt.subplot(1, int(days / 1440), 1)
        plt.ylabel('hour', size=22)

        plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0, hspace=0)

        # Output figure
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
