#coding='UTF-8'

from bs4 import BeautifulSoup
import threading,pymysql,time,requests,os,urllib3,re
requests.packages.urllib3.disable_warnings()
requests.adapters.DEFAULT_RETRIES = 5

class Spider():
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/65.0.3325.181 Safari/537.36',
        'Referer': "https://beauty.coding.ee/"
    }
    page_url_list = []
    img_url_list = []
    rlock = threading.RLock()
    s=requests.session()
    s.keep_alive = False
    dbhost={
        "host":"127.0.0.1",
        "dbname":"silumz",
        "user":"root",
        "password":"root"
    }

    def __init__(self,page_number=10,img_path='imgdir',thread_number=5,type='meitui',type_id=1):
        self.spider_url = 'https://beauty.coding.ee/'
        self.page_number = int(page_number)
        self.img_path = img_path
        self.thread_num = thread_number
        self.type_id = type_id
        self.type=type

    def get_url(self):
        for i in range(1, self.page_number+1):
            if i == 1:
                page = self.s.get(self.spider_url + self.type, verify=False).text
            else:
                data = {
                    "categorySlug": self.type,
                    "currentPage": i
                }
                page = self.s.post(self.spider_url, data=data, verify=False).text
            soup = BeautifulSoup(page, "html.parser").find("div", class_="main").find_all("dt")
            for pages in soup:
                page_url = pages.find("a").get("href")
                url = self.spider_url + page_url
                self.page_url_list.append(url)

    def get_img_url(self):
        db = pymysql.connect(self.dbhost.get("host"), self.dbhost.get("user"), self.dbhost.get("password"),
                             self.dbhost.get("dbname"))
        cursor = db.cursor()
        while True:
            self.rlock.acquire()
            if len(self.page_url_list) == 0:
                self.rlock.release()
                break
            else:
                page_url=self.page_url_list.pop()
                self.rlock.release()
                try:
                    tagidlist = []
                    page = self.s.get(page_url, verify=False).text
                    soup = BeautifulSoup(page, "html.parser")
                    img = soup.find("div", id="picbox").find("img").get("src")
                    title=soup.find("div",class_="title").find("h2").text
                    isExists = cursor.execute("SELECT title FROM images_page WHERE title =" + "'" + title + "'" + " limit 1;")
                    if isExists != 0:
                        print("已采集：" + title)
                    else:
                        taglist = re.findall('<meta name="keywords" content="(.*?)" />', page)
                        for tags in taglist:
                            for tag in tags.split(","):
                                sqltag = "SELECT * FROM images_tag WHERE tag =" + "'" + tag + "'" + " limit 1;"
                                isExiststag = cursor.execute(sqltag)
                                if isExiststag == 0:
                                    cursor.execute("INSERT INTO images_tag (tag) VALUES (%s)", tag)
                                cursor.execute("SELECT id FROM images_tag WHERE tag =" + "'" + tag + "'")
                                for id in cursor.fetchall():
                                    tagidlist.append(id[0])
                        p = (title, str(tagidlist), time.strftime('%Y-%m-%d', time.localtime(time.time())), self.type_id, "1",page_url)
                        cursor.execute("INSERT INTO images_page (title,tagid,sendtime,typeid,firstimg,crawler) VALUES (%s,%s,%s,%s,%s,%s)", p)
                        print("开始采集：" + title)
                        pageid = cursor.lastrowid
                        img_base_url = "/".join(img.split("/")[0:-1]) + "/"
                        img_num_soup=soup.find("span", id="picCount").text
                        num_re=re.compile(r'\d+')
                        img_num =num_re.findall(img_num_soup)[0]
                        for i in range(1, int(img_num)):
                            url = img_base_url + str(i) + ".jpg"
                            img_loc_path = self.img_path +time.strftime('%Y%m%d', time.localtime(
                                    time.time())) + "/"+"/".join(url.split("/")[-2:])
                            if i == 1:
                                cursor.execute(
                                    "UPDATE images_page SET firstimg = " + "'" + img_loc_path + "'" + " WHERE title=" + "'" + title + "'")
                            imgp = pageid, img_loc_path,url
                            cursor.execute("INSERT INTO images_image (pageid,imageurl,originurl) VALUES (%s,%s,%s)", imgp)
                            self.img_url_list.append({"url":url,"path":img_loc_path,"referer":page_url})
                except Exception as e:
                    self.page_url_list.append(page_url)
                    print(e)
        db.close()

    def down_img(self,imgsrc,imgpath,referer):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36",
            "Referer": referer
        }
        isdata = os.path.exists(".." +"/".join(imgpath.split("/")[0:-1]))
        if not isdata:
            os.makedirs(".." + "/".join(imgpath.split("/")[0:-1]))
        with open(".." + imgpath, "wb")as f:
            f.write(requests.get(imgsrc, headers=headers,verify=False).content)
            print("下载图片：" + imgpath)

    def down_url(self):
        while True:
            Spider.rlock.acquire()
            if len(Spider.img_url_list) == 0:
                Spider.rlock.release()
                break
            else:
                img_url = Spider.img_url_list.pop()
                Spider.rlock.release()
                try:
                    url=img_url.get("url")
                    path=img_url.get("path")
                    referer=img_url.get("referer")
                    self.down_img(url,path,referer)
                except Exception as e:
                    print(e)
                    self.img_url_list.append({"url":img_url.get("url"),"path":img_url.get("path"),"referer":img_url.get("referer")})
                    pass


    def run_1(self):
        # 启动thread_num个进程来爬去具体的img url 链接
        url_threa_list=[]
        for th in range(self.thread_num):
            add_pic_t = threading.Thread(target=self.get_img_url)
            url_threa_list.append(add_pic_t)

        for t in url_threa_list:
            t.setDaemon(True)
            t.start()

        for t in url_threa_list:
            t.join()

    def run_2(self):
        # 启动thread_num个来下载图片
        for img_th in range(self.thread_num):
            download_t = threading.Thread(target=self.down_url)
            download_t.start()

if __name__ == '__main__':
    for i in [{"page":1,"type":"xinggan","type_id":1},{"page":1,"type":"meitui","type_id":2},{"page":1,"type":"qingchun","type_id":3}]:
        spider = Spider(page_number=i.get("page"), img_path='/static/images/', thread_number=10,type=i.get("type"),type_id=i.get("type_id"))
        spider.get_url()
        spider.run_1()
        spider.run_2()
