from bs4 import BeautifulSoup
import requests
import re

response = requests.get("https://movies.yahoo.com.tw/chart.html?cate=rating", headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit 537.36 (KHTML, like Gecko) Chrome"})
soup = BeautifulSoup(response.text, "html.parser").find("div", id="maincontainer").find_all("div")[99] # 電影排行榜
movie_name = []
movie_date = []
movie_star = []
movie_link = []
movie_info = []
import_data = "{% extends \"base.html\" %}\n"
box1_start = "{% block box1 %}"
box1_end = "{% endblock box1 %}"

def get_data():
    #取得排行榜電影名稱
    movie_name.append(soup.find("h2").text)
    for name in soup.find_all("div", class_ = "rank_txt"):
        movie_name.append(name.text)

    #取得電影上映日
    for date in soup.find_all("div", text=re.compile("^[1-9]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])$")):
        movie_date.append(date.text)

    #取得電影評分
    for star in soup.find_all("h6", class_ = "count"):
        movie_star.append(star.text)

    #取得電影連結
    for data in soup.find_all("a", href=re.compile("^https://movies.yahoo.com.tw/movieinfo_main/")):
        movie_link.append(data.get("href"))

    #取得電影介紹
    for link in movie_link:
        mov_res = requests.get(link,headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit 537.36 (KHTML, like Gecko) Chrome"})
        mov_soup = BeautifulSoup(mov_res.text, "html.parser")
        movie_info.append(mov_soup.find("div", class_="gray_infobox_inner").find("span", id="story").text.lstrip().replace('\r\n', '<br/>').replace('\n', '').replace(u'\xa0', u' '))

def write_html():
    get_data()
    buff = [import_data, box1_start]
    for i in range(len(movie_name)):
        buff.append("\n\t<div class=\"box\">\n")
        buff.append("\t\t<a href=\""+ movie_link[i] + "\"><p>" + movie_name[i] + "</p></a>\n")
        buff.append("\t\t<p>" + "上映日 : " + movie_date[i] + "</p>\n")
        buff.append("\t\t<p>" + "評分 : " + movie_star[i] + "</p>\n")
        buff.append("\t\t<button id=\"myBtn\">了解更多</button>\n")
        buff.append("\t\t<div id=\"myModal\" class=\"modal\">\n")
        buff.append("\t\t\t<div class=\"modal-content\" style=\"margin-top: 20%!important; height: 40%;\">\n")
        buff.append("\t\t\t\t<span class=\"close\">&times;</span>\n")
        buff.append("\t\t\t\t<p style=\"text-align: left; margin-left: 5%; margin-right: 5%;\">\n")
        buff.append("\t\t\t\t\t" + movie_info[i] + "\n")
        buff.append("\t\t\t\t</p>\n\t\t\t</div>\n\t\t</div>\n\t</div>\n")
    buff.append(box1_end)
    try:
        file = open("./templates/index.html", "w")
        file.writelines(buff)
        file.close()
    except IOError:
        input("Could not open file! Press Enter to retry.")

write_html()