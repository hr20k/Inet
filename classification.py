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

def data_classification(data):
    classify = []
    sum = [0]*4
    now = data[0]['datetime']

    for day in data:
        # 日にちが変わったら更新
        difference = day['datetime'] - now
        if difference.days > 0:

            for i in range(len(sum)):
                sum[i] *= 100 / 1440
            t = {'datetime': now,
                 'classify': sum}
            classify.append(t)
            now = day['datetime']
            sum = [0]*4

        # データがない場合0置換
        if day['id1'] == 'x' or day['id1'] == 'X':
            day['id1'] = '0'
        if day['id2'] == 'x' or day['id2'] == 'X':
            day['id2'] = '0'

        # 10進数変換
        day['id1'] = int(day['id1'], 16)
        day['id2'] = int(day['id2'], 16)

        if day['id1'] == 0 and day['id2'] == 0: # xx
            sum[0] += 1
        elif day['id1'] != 0 and day['id2'] == 0: # ox
            sum[1] += 1
        elif day['id1'] == 0 and day['id2'] != 0: # xo
            sum[2] += 1
        else: # oo
            sum[3] += 1
    for i in range(len(sum)):
        sum[i] *= 100 / 1440
    t = {'datetime': now,
         'classify': sum}
    classify.append(t)

    return classify

def figuer_plot(data):
    left = [i for i in range(1,len(data)+1)]
    height_xx = [i['classify'][0] for i in data]
    height_ox = [i['classify'][1] for i in data]
    height_xo = [i['classify'][2] for i in data]
    height_oo = [i['classify'][3] for i in data]
    labels = [str(i['datetime'].month) + '/' + str(i['datetime'].day) for i in data]

    plt.bar(left, height_oo, align='center', color='#FFA0A0', label='id1 & id2')
    plt.bar(left, height_ox, align='center', color='#A0A0FF', label='id1', bottom=height_oo)
    plt.bar(left, height_xo, align='center', color='#A3EF3F', label='id2', bottom=[i+j for i,j in zip(height_oo,height_ox)])
    # plt.bar(left, height_xx, align='center', color='#202E41', bottom=[i+j+k for i,j,k in zip(height_oo,height_xo,height_ox)])
    plt.xticks(left, labels)  # 横軸ラベル
    plt.legend()
    plt.ylabel('Rate[%]')

    plt.show()


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
    figuer_plot(classify)

if __name__ == '__main__':
    main()