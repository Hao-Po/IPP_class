import requests
import re
from bs4 import BeautifulSoup
from opencc import OpenCC # 簡繁轉換

douban_names = [] # 存電影名
douban_links = [] # 存往內一層的URL
douban_dates = [] # 存上映時間
douban_scores = [] # 存評分
douban_movieInfo = [] # 存電影介紹
headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit 537.36 (KHTML, like Gecko) Chrome"}

def get_douban():
    cc = OpenCC("s2tw") # 簡體轉繁體

    response = requests.get(url = "https://movie.douban.com/chart", headers = headers) # 豆瓣
    soup = BeautifulSoup(response.text, "lxml")
    for item in soup.find_all("div","pl2"):
        douban_names.append(cc.convert(item.find("a","").find("span").text))
        douban_dates.append(cc.convert(item.find("p","pl").text.split("/")[0]))
        douban_scores.append(item.find("div","star clearfix").find("span","rating_nums").text)
    for item in soup.find_all("table"):
        douban_links.append(item.find("a").get('href'))

    for url in douban_links: # 為了電影介紹往內爬一層
        response = requests.get(url = url, headers = headers) 
        soup = BeautifulSoup(response.text, "lxml")
        douban_movieInfo.append(cc.convert(soup.find("div","related-info").find("span","").text.replace(" ","").replace("\n","").replace("　","")))
    # print("--------------------Douban--------------------")
    # print(douban_names)
    # print(douban_dates)
    # print(douban_scores)
    # print(douban_movieInfo)
    # print("----------------------------------------------")


ptt_names = [] # 存電影名
ptt_links = [] # 存往內一層的URL
ptt_dates = [] # 存上映時間
ptt_scores = [] # 存評分
ptt_movieInfo = [] # 存電影介紹

def get_ptt():
    response = requests.get(url = "https://www.movier.tw/latest.php?order=hot", headers = headers) # PTT
    soup = BeautifulSoup(response.text, "lxml")
    info_items = soup.find("div","row-fluid well").find_all("tr")
    new_info_items = iter(info_items)
    next(new_info_items)

    for item in new_info_items:
        ptt_names.append(item.find("a").find("h3").text)
        ptt_links.append(item.find("a").get('href'))
        ptt_scores.append(item.find("span").text)

    for i in range(0,len(ptt_names)): # 把電影名稱英文部分拿掉
        ptt_names[i] = ptt_names[i].split("(")[0]

    for url in ptt_links: # 為了電影介紹往內爬一層
        ptt_temp_movieInfo = []
        ptt_new_temp_movieInfo = []
        response = requests.get(url = "https://www.movier.tw/"+url, headers = headers)
        soup = BeautifulSoup(response.text, "lxml")
        for info in soup.find_all("dl","dl-horizontal"):
            ptt_temp_movieInfo.append(info.text.replace("　","").replace("\r","").split("\n"))
        for temp_1 in ptt_temp_movieInfo:
            for temp_2 in temp_1:
                if temp_2 == '' or temp_2 == 'N/A' or temp_2 == '\r':
                    continue
                else:
                    ptt_new_temp_movieInfo.append(temp_2)

        if '上映日期' not in ptt_new_temp_movieInfo:
            ptt_dates.append("")
        else:
            for i in range(0,len(ptt_new_temp_movieInfo)):
                if ptt_new_temp_movieInfo[i] == '上映日期':
                    ptt_dates.append(ptt_new_temp_movieInfo[i+1])
        if '簡介' not in ptt_new_temp_movieInfo:
            ptt_movieInfo.append("")
        else:
            for i in range(0,len(ptt_new_temp_movieInfo)):
                if ptt_new_temp_movieInfo[i] == '簡介':
                    ptt_movieInfo.append(ptt_new_temp_movieInfo[i+1].strip())

    # print("----------------------PTT----------------------")
    # print(len(ptt_names))
    # print(len(ptt_scores))
    # print(len(ptt_dates))
    # print(len(ptt_movieInfo))
    # print("-----------------------------------------------")

yahoo_names = [] # 存電影名
yahoo_links = [] # 存往內一層的URL
yahoo_dates = [] # 存上映時間
yahoo_scores = [] # 存評分
yahoo_movieInfo = [] # 存電影介紹

def get_yahoo():
    response = requests.get("https://movies.yahoo.com.tw/chart.html?cate=rating", headers = headers)
    soup = BeautifulSoup(response.text, "html.parser").find("div", id="maincontainer").find_all("div")[99] # 電影排行榜

    #取得排行榜電影名稱
    yahoo_names.append(soup.find("h2").text)
    for name in soup.find_all("div", class_ = "rank_txt"):
        yahoo_names.append(name.text)

    #取得電影上映日
    for date in soup.find_all("div", text=re.compile("^[1-9]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])$")):
        yahoo_dates.append(date.text)

    #取得電影評分
    for star in soup.find_all("h6", class_ = "count"):
        yahoo_scores.append(star.text)

    #取得電影連結
    for data in soup.find_all("a", href=re.compile("^https://movies.yahoo.com.tw/movieinfo_main/")):
        yahoo_links.append(data.get("href"))

    #取得電影介紹
    for link in yahoo_links:
        mov_res = requests.get(link, headers = headers)
        mov_soup = BeautifulSoup(mov_res.text, "html.parser")
        yahoo_movieInfo.append(mov_soup.find("div", class_="gray_infobox_inner").find("span", id="story").text.lstrip().replace('\n', '').replace('\r', '').replace(u'\xa0', u' '))

    # print("---------------------YAHOO---------------------")
    # print(yahoo_names)
    # print(yahoo_scores)
    # print(yahoo_dates)
    # print(yahoo_movieInfo)
    # print("-----------------------------------------------")

def write_html():
    get_yahoo()
    get_douban()
    get_ptt()
    buff = []
    buff.append("{% extends \"base.html\" %}\n{% block box1 %}")
    for i in range(len(yahoo_names)):
        buff.append("\n\t<div class=\"box\">\n")
        buff.append("\t\t<a href=\""+ yahoo_links[i] + "\"><p>" + yahoo_names[i] + "</p></a>\n")
        buff.append("\t\t<p>" + "上映日 : " + yahoo_dates[i] + "</p>\n")
        buff.append("\t\t<p>" + "評分 : " + yahoo_scores[i] + "/5</p>\n")
        buff.append("\t\t<button id=\"yahoo" + str(i) + "\" onclick=\"getBtnId(" + "'yahoo" + str(i) + "', " + str(i) + ")\">了解更多</button>\n")
        buff.append("\t\t<div id=\"myahoo" + str(i) + "\" class=\"modal\">\n")
        buff.append("\t\t\t<div class=\"modal-content\" style=\"margin-top: 20%!important; height: 3%; position:fixed;\">\n")
        buff.append("\t\t\t\t<p style=\"text-align: left; margin-left: 5%; margin-right: 5%;\">\n")
        buff.append("\t\t\t\t\t" + yahoo_movieInfo[i] + "\n")
        buff.append("\t\t\t\t</p>\n\t\t\t</div>\n\t\t</div>\n\t</div>\n")
    buff.append("{% endblock box1 %}\n")

    buff.append("{% block box2 %}")
    for i in range(len(douban_names)):
        buff.append("\n\t<div class=\"box\">\n")
        buff.append("\t\t<a href=\""+ douban_links[i] + "\"><p>" + douban_names[i] + "</p></a>\n")
        buff.append("\t\t<p>" + "上映日 : " + douban_dates[i] + "</p>\n")
        buff.append("\t\t<p>" + "評分 : " + douban_scores[i] + "/10</p>\n")
        buff.append("\t\t<button id=\"douban" + str(i) + "\" onclick=\"getBtnId(" + "'douban" + str(i) + "', " + str(i+len(yahoo_names)) + ")\">了解更多</button>\n")
        buff.append("\t\t<div id=\"mdouban" + str(i) + "\" class=\"modal\">\n")
        buff.append("\t\t\t<div class=\"modal-content\" style=\"margin-top: 20%!important; height: 3%; position:fixed;\">\n")
        buff.append("\t\t\t\t<p style=\"text-align: left; margin-left: 5%; margin-right: 5%;\">\n")
        buff.append("\t\t\t\t\t" + douban_movieInfo[i] + "\n")
        buff.append("\t\t\t\t</p>\n\t\t\t</div>\n\t\t</div>\n\t</div>\n")
    buff.append("{% endblock box2 %}")

    buff.append("{% block box3 %}")
    for i in range(len(ptt_names)):
        buff.append("\n\t<div class=\"box\">\n")
        buff.append("\t\t<a href=\""+ ptt_links[i] + "\"><p>" + ptt_names[i] + "</p></a>\n")
        buff.append("\t\t<p>" + "上映日 : " + ptt_dates[i] + "</p>\n")
        buff.append("\t\t<p>" + "評分 : " + ptt_scores[i] + "/100</p>\n")
        buff.append("\t\t<button id=\"ptt" + str(i) + "\" onclick=\"getBtnId(" + "'ptt" + str(i) + "', " + str(i+len(yahoo_names)+len(douban_names)) + ")\">了解更多</button>\n")
        buff.append("\t\t<div id=\"mptt" + str(i) + "\" class=\"modal\">\n")
        buff.append("\t\t\t<div class=\"modal-content\" style=\"margin-top: 20%!important; height: 3%; position:fixed;\">\n")
        buff.append("\t\t\t\t<p style=\"text-align: left; margin-left: 5%; margin-right: 5%;\">\n")
        buff.append("\t\t\t\t\t" + ptt_movieInfo[i] + "\n")
        buff.append("\t\t\t\t</p>\n\t\t\t</div>\n\t\t</div>\n\t</div>\n")
    buff.append("{% endblock box3 %}")
    try:
        file = open("./templates/index.html", "w")
        file.writelines(buff)
        file.close()
    except IOError:
        input("Could not open file! Press Enter to retry.")