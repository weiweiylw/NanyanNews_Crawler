# encoding: UTF-8

import urllib2
from bs4 import BeautifulSoup

import MySQLdb
import MySQLdb.cursors

import chardet

import time

import sys
reload(sys)
sys.setdefaultencoding('utf8')

def getPageCount():
    url = "http://sam.pkusz.edu.cn/index.php?m=content&c=index&a=lists&catid=408"
    response = urllib2.urlopen(url)
    html = response.read()

    soup = BeautifulSoup(html)
    #print soup
    
    #获取总页数
    pages = soup.find(attrs={'id':'page'})
    #print pages
    
    page = pages.find_all('a')
    
    #倒数第二个元素
    pageCount = int(page[-2].string)
    #print pageCount
    
    return pageCount
    
def getNewsUrls(pageCount):

    #print type(pageCount)
    urls = []
    
    for page in range(pageCount):
        #print type(page)
        url = "http://sam.pkusz.edu.cn/index.php?m=content&c=index&a=lists&catid=408&page=%d" % (page + 1)
        response = urllib2.urlopen(url)
        html = response.read()

        soup = BeautifulSoup(html)

        #lists = soup.find(attrs={'id':'dt_right'})
        #title_content = lists.find_all(id='dt_1')

        url_all = soup.find_all(id='dt_1')
        #print title_all
        for url_content in url_all:
            url = url_content.contents[5].a['href']
            urls.append(url)
        #print urls
    return urls

def parseNews(urlList):
    news = []
    
    for url in urlList:
        try:
            newsItem = {}
            
            response = urllib2.urlopen(url)
            html = response.read()

            soup = BeautifulSoup(html)

            article = soup.find(attrs={'id': 'dt_right'})
            #print article

            title = soup.find(attrs={'class': 'new_tit'}).string
            #print title
            
            #string, contents
            #编码问题
            #date = article.find(attrs={'class': 'tips'}).contents[0].split('|')[0]
            #print date

            content = soup.find(attrs={'class': 'new_nr'})
            #print content

            foot = soup.find(attrs={'id': 'foot'})
            clicks_url = foot.find_previous_sibling()['src']
            #print clicks_url

            #找到获取点击率的js链接

            response = urllib2.urlopen(clicks_url)
            clicks = response.read().split('\'')[-2]
            #print clicks             

            newsItem['title'] = title.encode('utf-8')

            #日期在url列表也就是标题页显示，没有再内容页显示，需单独获取

            newsItem['date'] = '2015-12-05'
            newsItem['content'] = content.encode('utf-8')
            newsItem['clicks'] = clicks
            #print newsItem
            news.append(newsItem)
        #有一个页面只有一个 PDF 文件，跳过
            
        except AttributeError:
            pass

    print news
    return news


def newsToMySQL(newsList):

    # 打开数据库连接
    db = MySQLdb.connect("localhost","root","","opensns", charset = 'utf8')

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    sql_checkDate = "select create_time from news where category=7 order by create_time desc limit 1"
    cursor.execute(sql_checkDate)
    result = cursor.fetchall()
    if (result):
        latest_date = result[0][0]
    else:
        latest_date = 0
    #print result[0][0]

    for item in newsList:
        #print item['content'].encode('gbk')
        #print '\n'
        #print chardet.detect(item['content'])
        
        #将datetime转换为时间戳：
        a = item['date'];
        #将其转换为时间数组
        timeArray = time.strptime(a, "%Y-%m-%d")
        #转换为时间戳
        timeStamp = int(time.mktime(timeArray))

        if (timeStamp > latest_date):

            sql = "INSERT INTO news(uid, title, category, status, view, dead_line, create_time) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % ('1', item['title'], '7', '1', item['clicks'] ,'2147483640', timeStamp)
            
            try:
               # 执行sql语句
               cursor.execute(sql)
               #print "ID of last record is ", int(cursor.lastrowid) #最后插入行的主键ID  

               sql_detail = "INSERT INTO news_detail(news_id, content) VALUES (%d, '%s')" % (int(cursor.lastrowid), item['content'])
               cursor.execute(sql_detail)

               # 提交到数据库执行
               db.commit()
            except:
               # Rollback in case there is any error
               db.rollback()

    # 关闭数据库连接
    db.close()

if __name__ == '__main__': 
    pageCount = getPageCount()
    #print pageCount
    urls = getNewsUrls(pageCount)
    #print len(urls)
    news = parseNews(urls)
    #print news
    newsToMySQL(news)