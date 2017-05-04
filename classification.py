import argparse
import datetime
import csv
import numpy as np
import matplotlib.pyplot as plt

def load_inet_data(fname):
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

def type_split(a,b):
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

        t = type_split(day['id1'],day['id2'])

        if t == 'xx': # xx
            sum[0] += 1
        elif t == 'ox': # ox
            sum[1] += 1
        elif t == 'xo': # xo
            sum[2] += 1
        else: # oo
            sum[3] += 1

    for i in range(len(sum)):
        sum[i] *= 100 / 1440
    t = {'datetime': now,
         'classify': sum}
    classify.append(t)

    return classify

def figuer_plot_rate(data):
    t = data[1]['datetime'] - data[0]['datetime']
    if t.days == 1:
        type = 'Day'
    elif t.seconds == 3600:
        type = 'Hour'
    left = [i for i in range(1,len(data)+1)]
    # height_xx = [i['classify'][0] for i in data]
    height_ox = [i['classify'][1] for i in data]
    height_xo = [i['classify'][2] for i in data]
    height_oo = [i['classify'][3] for i in data]
    if type == 'Day':
        labels = [str(i['datetime'].month) + '/' + str(i['datetime'].day) for i in data]
    else:
        labels = [i['datetime'].hour for i in data]

    plt.bar(left, height_oo, align='center', color='#FFA0A0', label='id1 & id2')
    plt.bar(left, height_ox, align='center', color='#A0A0FF', label='id1', bottom=height_oo)
    plt.bar(left, height_xo, align='center', color='#A3EF3F', label='id2', bottom=[i+j for i,j in zip(height_oo,height_ox)])
    # plt.bar(left, height_xx, align='center', color='#202E41', bottom=[i+j+k for i,j,k in zip(height_oo,height_xo,height_ox)])
    plt.xticks(left, labels)
    plt.legend()
    plt.ylabel('Rate[%]')

    plt.show()

def figuer_plot_activity(data):
    _data = []
    _frame = type_split(data[0]['id1'],data[0]['id2'])
    sum = 0
    cnt = -1
    now = data[0]['datetime'] + datetime.timedelta(days=-1)

    for day in data:
        # 日にちが変わったら更新
        difference = day['datetime'] - now
        if difference.days == 1:
            _data.append([])
            _frame = type_split(day['id1'],day['id2'])
            sum = 0
            cnt += 1
            now = day['datetime']

        frame = type_split(day['id1'],day['id2'])
        if frame == _frame:
            sum += 1
        else:
            t = {'data': sum,
                'count': _frame}
            sum = 1
            _data[cnt].append(t)

        _frame = frame

    return _data

def main():
    # 引数からファイル名を取得
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv_file")
    parser.add_argument("--encoding", default="utf_8")
    options = parser.parse_args()
    print(options.input_csv_file)
    fname = options.input_csv_file

    i_data = load_inet_data(fname)
    classify = data_classification(i_data)
    # figuer_plot_rate(classify)
    figuer_plot_activity(i_data)

if __name__ == '__main__':
    main()