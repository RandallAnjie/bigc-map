import os
import json
import tkinter
import turtle
from collections import defaultdict
from heapq import heappop, heappush
from math import sqrt
from tkinter import *
from tkinter.ttk import Combobox
import requests


def get_record(url):
    """
    通过url拿到json
    :param url: json文件url
    :return: json
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Failed to retrieve data from {url}. HTTP Status Code: {response.status_code}')
        return None


def download_file(url, local_filename):
    """
    下载文件
    :param url: 下载文件url
    :param local_filename: 文件名称
    :return: 文件
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134'
    }
    with requests.get(url, headers=headers, stream=True) as r:
        r.raise_for_status()  # Check if the request was successful
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)


# 从点str1移动到str2
def move(str1, str2):
    x = point[str1][0] - 953 / 2
    y = 759 / 2 - point[str1][1]
    a = point[str2][0] - 953 / 2
    b = 759 / 2 - point[str2][1]
    turtle.up()
    turtle.goto(x, y)
    turtle.down()
    turtle.goto(a, b)
    turtle.up()


# 判断两点的距离
def distence(str1, str2, paramein, pointin):
    if [str1, str2] in paramein or [str2, str1] in paramein:
        return sqrt((pointin[str1][1] - pointin[str2][1]) ** 2 + (pointin[str1][0] - pointin[str2][0]) ** 2)
    elif pointin[str1][0] == pointin[str2][0]:
        return abs(pointin[str1][1] - pointin[str2][1])
    elif pointin[str1][1] == pointin[str2][1]:
        return abs(pointin[str1][0] - pointin[str2][0])
    else:
        return 1E100


# 优化后Dijkstra算法
def dijkstra(edges, t, f):
    g = defaultdict(list)
    for l, r, c in edges:
        g[l].append((c, r))
    q, seen, mins = [(0, f, [])], set(), {f: 0}
    while q:
        (cost, v1, path) = heappop(q)
        if v1 not in seen:
            seen.add(v1)
            path = [v1] + path
            if v1 == t:
                return cost, path
            for c, v2 in g.get(v1, ()):
                if v2 in seen:
                    continue
                prev = mins.get(v2, None)
                next = cost + c
                if prev is None or next < prev:
                    mins[v2] = next
                    heappush(q, (next, v2, path))
    return float("inf"), []


def draw(value):
    # 初始化地图
    turtle.setup(width=953, height=759, startx=50, starty=30)
    turtle.clear()
    turtle.title("导航路线")
    # 图片URL
    url = 'https://randallanjie.com/json/bigc.png'
    filename = os.path.basename(url)
    local_path = os.path.join("./", filename)

    # Check if the file already exists
    if not os.path.isfile(local_path):
        try:
            print("地图下载中")
            download_file(url, './bigc.png')
        except Exception as e:
            print(f'\n{url} 下载失败！\n{e}')
            tkinter.messagebox.showinfo('提示', '下载地图失败，请重试！')
        else:
            print("地图下载完成！")
    else:
        print("地图已经存在！")
    turtle.bgpic("./bigc.png")
    turtle.pensize(15)
    turtle.color("#ff0000")
    turtle.hideturtle()
    for i in range(len(value[1]) - 1):
        move(value[1][i], value[1][i + 1])
    turtle.mainloop()
    # turtle.bye()


# 进度条迭代
def progressbar(cur, total=100):
    percent = '{:.2%}'.format(cur / total)
    sys.stdout.write('\r')
    sys.stdout.write("[%-100s] %s" % ('=' * int(cur), percent))
    sys.stdout.flush()


# 进度条
def schedule(blocknum, blocksize, totalsize):
    """
    blocknum:当前已经下载的块
    blocksize:每次传输的块大小
    totalsize:网页文件总大小
    """
    if totalsize == 0:
        percent = 0
    else:
        percent = blocknum * blocksize / totalsize
    if percent > 1.0:
        percent = 1.0
    percent = percent * 100
    progressbar(percent)


# 初始化
def init():
    # 特殊连线点
    parame = get_record('https://randallanjie.com/json/parame.json')
    # 各个点在地图上的坐标
    pointin = get_record('https://randallanjie.com/json/point.json')
    # 复选框的值
    valuesin = get_record('https://randallanjie.com/json/values.json')
    # 根据两点距离将相邻的两个点存入matrix
    matrix = []
    for i in pointin:
        for j in pointin:
            if distence(i, j, parame, pointin) != 0 and distence(i, j, parame, pointin) != 1E100:
                matrix.append((i, j, distence(i, j, parame, pointin)))
    return pointin, valuesin, matrix


# 点击按钮运行部分
def calc(a, b):
    x = dijkstra(listview, a, b)
    print(x)
    try:
        draw(x)
    except turtle.Terminator:
        draw(x)


print("开始初始化")
point, values, listview = init()
root = Tk()
root.title('北京印刷学院导航系统')
root.geometry('320x50')
var1 = StringVar()
var2 = StringVar()
comb1 = Combobox(root, textvariable=var1, values=values, state='readonly')
comb2 = Combobox(root, textvariable=var2, values=values, state='readonly')
comb1.place(relx=0.1, rely=0.25, relwidth=0.2)
comb2.place(relx=0.4, rely=0.25, relwidth=0.2)
btn = Button(root, text="导航", command=lambda: calc(comb1.get(), comb2.get()))
btn.place(relx=0.7, rely=0.25, relwidth=0.2)
root.mainloop()
