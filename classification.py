import argparse
import datetime
import csv

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
            t = {'datetime': now,
                 'classify': [sum[0],sum[1],sum[2],sum[3]]}
            classify.append(t)
            now = day['datetime']
            sum = [0]*4

        # データがない場合0置換
        if day['id1'] == 'x' or day['id1'] == 'X':
            day['id1'] = 0

        # 10進数変換
        day['id1'] = int(day['id1'], 16)
        day['id2'] = int(day['id2'], 16)

        if day['id1'] == 0 and day['id2'] == 0:
            sum[0] += 1
        elif day['id1'] != 0 and day['id2'] == 0:
            sum[1] += 1
        elif day['id1'] == 0 and day['id2'] != 0:
            sum[2] += 1
        else:
            sum[3] += 1
    t = {'datetime': now,
         'classify': [sum[0], sum[1], sum[2], sum[3]]}
    classify.append(t)

    return classify

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
    for i in classify:
        print(i)

if __name__ == '__main__':
    main()