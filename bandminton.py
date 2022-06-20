# -*- coding: utf-8 -*-

import random
import requests
import re
import time
from bs4 import BeautifulSoup as bs
import json
import urllib
from libhustpass import login
from urllib.parse import quote

"""
预约羽毛球系统脚本，首先设置校园网登录参数和羽毛球场馆参数，请保证校园卡电子账户里有充足的金额。最好在早上8点预约（8点前有可能被拉入黑名单）。
"""


def save_html(text, file):
    with open(file, 'w') as f:
        f.write(text)


def Check(text):
    try:
        alarm = re.search(
            r"alert\(HTMLDecode\('(.*)'\), '提示信息'\);", text).group(1)
        print(alarm)
        return True
        # return alarm
    except:
        return False


# proxy = {"http": "http://127.0.0.1:8080"}
User_Agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"
headers = {"Origin": "https://pecg.hust.edu.cn",
           "User-Agent": User_Agent}
headers1 = {"Referer": "http://pecg.hust.edu.cn/cggl/",  # 来源网址，防止报非法操作
            "User-Agent": User_Agent}
headers2 = {"Referer": "http://pecg.hust.edu.cn/cggl/front/yuyuexz",
            "User-Agent": User_Agent}

### config ###
url = "https://pass.hust.edu.cn/cas/login?service=http%3A%2F%2Fpecg.hust.edu.cn%2Fcggl%2Findex1"
ticket = login("U10000000", "passward", url)
# time
allocDate = "2022-05-27"  # 日期，格式不要动
allocTimeStart = "16:00:00"  # 时间
allocTimeEnd = "18:00:00"

# partner
partnerName = "张三"  # 同伴
# print(quote(partnerName))
partnerID = "U100000393"  # 同伴学号
partnerPwd = "passward"  # 同伴密码
changName = "西体"

BookingHour = 8
BookingMin = 0
### config end ###

chang1 = 45
Num1 = 22
data1 = "110@{0}-{1},133@{0}-{1},215@{0}-{1},216@{0}-{1},218@{0}-{1},376@{0}-{1},217@{0}-{1},219@{0}-{1},\
220@{0}-{1},221@{0}-{1},222@{0}-{1},223@{0}-{1},224@{0}-{1},368@{0}-{1},369@{0}-{1},370@{0}-{1},\
377@{0}-{1},371@{0}-{1},372@{0}-{1},373@{0}-{1},374@{0}-{1},375@{0}-{1},".format(
    allocTimeStart, allocTimeEnd)

chang2 = 69
Num2 = 8
data2 = "300@{0}-{1},299@{0}-{1},298@{0}-{1},297@{0}-{1},301@{0}-{1},134@{0}-{1},295@{0}-{1},296@{0}-{1},".format(
    allocTimeStart, allocTimeEnd)


def main(chang, Num, data, ChangeChang=False):
    # f = open("log.txt", "w")
    mainSess = requests.session()
    mainSess.max_redirects = 10
    mainSess.get(ticket)
    while True:
        print("开始预约")
        mainSess.get("http://pecg.hust.edu.cn/cggl/")

        mainSess.get("http://pecg.hust.edu.cn/cggl/front/yuyuexz",
                     headers=headers1)

        htmlToken1 = None
        url_step1 = "http://pecg.hust.edu.cn/cggl/front/syqk?cdbh=%d&date=%s&starttime=%s&endtime=" % (
                    chang, allocDate, allocTimeStart)
        while htmlToken1 == None:
            try:
                htmlToken1 = mainSess.get(url_step1, headers=headers2)
            except Exception as e:
                print("time is not ok")
            # save_html(htmlToken1.text, "Token1.html")

        Token1 = re.search(
            r'\$\(this\)\.append\("<input class=\\"token\\" type=\\"hidden\\" name=\\"token\\" value=\\"(.*)\\" >"\);', htmlToken1.text).group(1)
        # print("获取登录Token为:", Token1)

        postData = {
            "changdibh": chang,
            "data": data,
            "date": allocDate,
            "time": time.strftime("%a %b %d %Y %H:%M:%S", time.localtime())+" GMT+0800 (中国标准时间)",
            "token": Token1
        }

        htmlToken2 = mainSess.post("http://pecg.hust.edu.cn/cggl/front/ajax/getsyzt", data=postData, headers={
                                   "Referer": url_step1, "User-Agent": User_Agent})

        print("获取场地信息", htmlToken2.text)
        json2 = json.loads(htmlToken2.text)
        token3 = json2[0]["token"]
        # for land in json2[0]["message"]:
        # for i in [2, 1, 6, 5, 3, 7, 0, 4]:
        Index = [i for i in range(Num)]
        # random.shuffle(Index)
        Count = 0
        for i in Index:
            land = json2[0]["message"][i]
            if land["zt"] != 1:
                print("Ground ", land["pian"], " is not avaliable")
                continue
            Count += 1
            print("Ground ", land["pian"], " is avaliable!!!")
            postData = {
                "starttime": allocTimeStart,
                "endtime": allocTimeEnd,
                "partnerCardType": "1",
                "partnerName": partnerName,
                "partnerSchoolNo": partnerID,
                "partnerPwd": partnerPwd,
                "choosetime": land["pian"],
                "changdibh": chang,  # 光谷体育馆
                "date": allocDate,
                "token": token3,
            }
            print(postData)
            try:
                midHtml = mainSess.post("http://pecg.hust.edu.cn/cggl/front/step2",
                                        data=postData, headers={"Referer": url_step1, "User-Agent": User_Agent})
            except Exception as e:
                print(e)
                print("time is not ok")
                continue

            # f.write(midHtml.text)
            print(midHtml)
            save_html(midHtml.text, "step2.html")

            if Check(midHtml.text):
                continue

            token4 = re.search(
                r'\$\(this\)\.append\("<input class=\\"token\\" type=\\"hidden\\" name=\\"token\\" value=\\"(.*)\\" >"\);', midHtml.text).group(1)
            parsedHtml = bs(midHtml.text, 'html.parser')

            if "请预约规定时间内的场地" in midHtml.text:
                print("Damn! 请预约规定时间内的场地")
                continue
            postData = dict()
            for entry in parsedHtml.find_all('input'):
                if entry.get("name") == "data":
                    postData["data"] = entry.get('value')
                if entry.get("name") == "id":
                    postData["id"] = entry.get('value')

            postData["token"] = token4

            # print(postData)

            postData["data"] = quote(postData["data"])

            postDataString = "&".join("%s=%s" % (
                k, v) for k, v in postData.items())+"&token="+postData["token"]

            headers3 = {
                "Referer": "http://pecg.hust.edu.cn/cggl/front/step2",
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "http://pecg.hust.edu.cn",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"
            }
            # 提交请求
            final_result = mainSess.post("http://pecg.hust.edu.cn/cggl/front/step3",
                                         data=postDataString, headers=headers3)
            # f.write(final_result.text)
            save_html(final_result.text, "step3.html")
            if Check(final_result.text):
                exit(0)
            if "您已预约成功" in final_result.text:
                print("预约成功！")
                # f.close()
                exit(0)
            else:
                print("预约失败！")

        if Count == 0 and ChangeChang == False:
            print("没有可预约的场")
            if chang == 45:
                chang, Num, data = chang2, Num2, data2
            else:
                chang, Num, data = chang1, Num1, data1
            ChangeChang = True
        elif Count == 0:
            print("西体，光体都不可预约，换个时间吧！")
            exit(0)
        # exit(0)


if __name__ == "__main__":
    if changName == "光体":
        chang, Num, data = chang1, Num1, data1
    else:
        chang, Num, data = chang2, Num2, data2

    print("开始定时")
    while(1):
        t = time.localtime()
        cur_hour, cur_min = t.tm_hour, t.tm_min
        print("\r", "倒计时{}分钟！".format((BookingHour-cur_hour)
              * 60+BookingMin-cur_min), end="", flush=True)
        if(cur_hour == BookingHour and cur_min == BookingMin):
            break
    print(time.localtime())
    main(chang, Num, data)
