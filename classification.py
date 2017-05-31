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


def type_split(a, b):
    """
    Input data format
    sensor data1, sensor data2 

    Return data
    'xx' or 'ox' or 'xo' or 'oo'
    """
    # データがない場合0置換
    if a == 'x' or a == 'X':
        a = '0'
    if b == 'x' or b == 'X':
        b = '0'

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


def data_classification(data, type='Day'):
    """
    Input data format (.csv)
    2000-01-01,00:00,0,0 (date, id1, id2)

    Return data format
    {'datetime': now, 'classify': sum} (sum = ['xx','ox','xo','oo'])
    """
    classify = []
    sum = [0]*4
    now = data[0]['datetime']

    for day in data:
        # 日にちが変わったら更新
        difference = day['datetime'] - now
        if difference.days == 1 and type == 'Day':
            for i in range(len(sum)):
                sum[i] *= 100 / 1440
            t = {'datetime': now,
                 'classify': sum}
            classify.append(t)
            now = day['datetime']
            sum = [0]*4
        elif difference.seconds == 3600 and type == 'Hour':
            for i in range(len(sum)):
                sum[i] *= 100 / 60
            t = {'datetime': now,
                 'classify': sum}
            classify.append(t)
            now = day['datetime']
            sum = [0]*4

        t = type_split(day['id1'], day['id2'])

        if t == 'xx':  # xx
            sum[0] += 1
        elif t == 'ox':  # ox
            sum[1] += 1
        elif t == 'xo':  # xo
            sum[2] += 1
        else:  # oo
            sum[3] += 1

    for i in range(len(sum)):
        sum[i] *= 100 / 1440
    t = {'datetime': now,
         'classify': sum}
    classify.append(t)

    return classify


def figuer_plot_rate(data):
    """
    Input data format
    data_classification() out put format
    """
    t = data[1]['datetime'] - data[0]['datetime']
    if t.days == 1:
        type = 'Day'
    elif t.seconds == 3600:
        type = 'Hour'

    x = 0
    while x < len(data):
        now = data[x]['datetime'].month
        days = 0
        while (x + days) < len(data):
            if now != data[x + days]['datetime'].month:
                break
            days += 1

        _data = data[x:x+days]

        plt.figure(figsize=(15, 10))
        left = [i for i in range(1, len(_data)+1)]
        # height_xx = [i['classify'][0] for i in data]
        height_ox = [i['classify'][1] for i in _data]
        height_xo = [i['classify'][2] for i in _data]
        height_oo = [i['classify'][3] for i in _data]
        if type == 'Day':
            labels = [i['datetime'].day for i in _data]
        else:
            labels = [i['datetime'].hour for i in _data]

        plt.bar(left, height_oo, align='center', color='#FFA0A0', label='id1 & id2')
        plt.bar(left, height_ox, align='center', color='#A0A0FF', label='id1', bottom=height_oo)
        plt.bar(left, height_xo, align='center', color='#A3EF3F', label='id2', \
                bottom=[i+j for i, j in zip(height_oo, height_ox)])
        # plt.bar(left, height_xx, align='center', color='#202E41', \
        #         bottom=[i+j+k for i, j, k in zip(height_oo, height_xo, height_ox)])
        plt.xticks(left, labels)
        plt.title(str(data[x]['datetime'].year) + '-' + str(data[x]['datetime'].month))
        plt.legend(loc='upper right')
        plt.ylabel('Rate[%]')

        plt.savefig(str(data[x]['datetime'].year) + '-' + str(data[x]['datetime'].month) + '.png')
        print(str(data[x]['datetime'].year) + '-' + str(data[x]['datetime'].month) + '.png')
        plt.close()
        # plt.show()
        x += days


def reshape_data(data):
    """
    Input data format
    2000-01-01,00:00,0,0 (date, id1, id2)
    
    Return data format
    {'data': sum, 'count': _frame} (_frame: 'xx','xo','ox','oo')
    """
    _data = []
    _frame = type_split(data[0]['id1'], data[0]['id2'])
    sum = 0
    cnt = -1
    now = data[0]['datetime'] + datetime.timedelta(days=-1)

    for day in data:
        # 日にちが変わったら更新
        difference = day['datetime'] - now
        if difference.days == 1:
            if day['datetime'] != data[0]['datetime']:
                t = {'data': sum,
                     'count': _frame}
                _data[cnt].append(t)

            _data.append([])
            _frame = type_split(day['id1'], day['id2'])
            sum = 0
            cnt += 1
            now = day['datetime']

        frame = type_split(day['id1'], day['id2'])
        if frame == _frame:
            sum += 1
        else:
            t = {'data': sum,
                 'count': _frame}
            sum = 1
            _data[cnt].append(t)

        _frame = frame

    t = {'data': sum,
         'count': _frame}
    _data[cnt].append(t)

    return _data


def figuer_plot_activity(data):
    """
    Input data format
    load_inet_data() return format (2000-01-01,00:00,0,0 (date, id1, id2))
    """
    _data = reshape_data(data)

    # グラフ線画
    a = 0
    while a < len(data):
        now = data[a]['datetime'].month
        days = 0
        while (a + days) < len(data):
            if now != data[a + days]['datetime'].month:
                break
            days += 1440

        bar = []
        x = 0
        for i in _data[int(a/1440):int(a + days/1440)]:
            bar.append([])
            for j in i:
                for k in ['xx', 'xo', 'ox', 'oo']:
                    if j['count'] == k:
                        bar[x].append(j['data'])
                    else:
                        bar[x].append(0)
            x += 1

        maxsize = 0
        for i in bar:
            if maxsize < len(i):
                maxsize = len(i)
        print('Maxsize: ' + str(maxsize))

        for i in range(len(bar)):
            bar[i] += [0]*(maxsize - len(bar[i]))

        bar = np.array(bar)
        print(bar)

        plt.figure(figsize=(15, 10))
        ind = np.arange(1, bar.shape[0]+1)
        labels = [i['datetime'].day for i in data[a:a+days:1440]]
        print(labels)
        width = 0.8
        bottom = np.zeros(bar.shape[0])
        colors = ['k', 'g', 'b', 'r']

        for i in range(bar.shape[1]):
            if i % 50 == 0:
                print(i)

            n = True
            for j in bar[:, i]:
                if j != 0:
                    n = False
                    break
            if n:
                continue

            plt.bar(ind,  # バーの左端と重なるx座標
                    bar[:, i]/60,  # バーの高さ
                    width,
                    bottom,  # バーが始まる高さ
                    color=colors[i % 4],  # 色
                    tick_label=labels,
                    align='center'
                    # label=label[i%4]  # 凡例用のラベル
                    )
            # 「積み上げ」を表現するための足場
            bottom += bar[:, i] / 60

        plt.ylabel('hour')
        plt.title(str(data[a]['datetime'].year) + '-' + str(data[a]['datetime'].month))
        plt.text(33.7, 23.5, 'id1,id2', size=17, weight='bold', ha='left', color='r')
        plt.text(33.7, 22.5, 'id1', size=17, weight='bold', ha='left', color='b')
        plt.text(33.7, 21.5, 'id2', size=17, weight='bold', ha='left', color='g')
        # plt.legend(loc="upper right")
        plt.xticks(ind, labels)

        # plt.show()
        plt.savefig(str(data[a]['datetime'].year) + '-' + str(data[a]['datetime'].month) + '_activity' + '.png')
        print(str(data[a]['datetime'].year) + '-' + str(data[a]['datetime'].month) + '_activity' + '.png')
        plt.close()
        a += days


def figuer_plot_activity1(fname, data):
    """
    Input data format
    load_inet_data() return format (2000-01-01,00:00,0,0 (date, id1, id2))
    """

    name, ext = os.path.splitext(fname)
    if not os.path.exists(name):
        os.mkdir(name)
    _data = reshape_data(data)

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
        colors = {'xx': 'k', 'xo': 'g', 'ox': 'b', 'oo': 'r'}
        labels = [i for i in range(1, int(days/1440 + 1))]
        print(labels)

        for i in range(int(days/1440)):
            bottom = 0

            # select subplot
            plt.subplot(1, int(days / 1440), i + 1)

            # Set xticks
            plt.xticks(range(1), (str(labels[i]),))

            # Set yticks
            plt.yticks(np.arange(0, 24, 6))

            # Set axes
            plt.gca().xaxis.set_ticks_position('none')
            if i == 0:
                plt.gca().spines['right'].set_visible(False)
                plt.gca().yaxis.set_ticks_position('left')
            elif i < int(days / 1440) - 1:
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
                    new_data[i][j]['data']/60,  # バーの高さ
                    width,
                    bottom,  # バーが始まる高さ
                    color=colors[new_data[i][j]['count']],  # 色
                    align='center'
                    )
                bottom += new_data[i][j]['data']/60

        # Set title
        plt.subplot(1, int(days / 1440), int(days / (1440 * 2)))
        plt.title(str(data[a]['datetime'].year) + '-' + str(data[a]['datetime'].month), size=22)

        # Set ylabel
        plt.subplot(1, int(days / 1440), 1)
        plt.ylabel('hour', size=22)

        # Print text
        plt.subplot(1, int(days / 1440), int(days / 1440))
        plt.text(1.3, 23.5, 'id1,id2', size=17, weight='bold', ha='left', color='r')
        plt.text(1.3, 22.5, 'id1', size=17, weight='bold', ha='left', color='b')
        plt.text(1.3, 21.5, 'id2', size=17, weight='bold', ha='left', color='g')

        plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0, hspace=0)

        # Output figure
        plt.savefig(str(name) + '/' + 'activity_' + str(data[a]['datetime'].year) + '-' + \
                    str(data[a]['datetime'].month) + '.png')
        print('activity_' + str(data[a]['datetime'].year) + '-' + str(data[a]['datetime'].month) + '.png')
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
    # classify = data_classification(i_data)
    # figuer_plot_rate(classify)
    # figuer_plot_activity(i_data)
    figuer_plot_activity1(fname, i_data)

if __name__ == '__main__':
    main()
