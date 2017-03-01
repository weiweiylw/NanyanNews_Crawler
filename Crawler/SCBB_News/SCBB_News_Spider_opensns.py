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
    url = "http://scbb.pkusz.edu.cn/index.php?m=content&c=index&a=lists&catid=862&page=1"
    response = urllib2.urlopen(url)
    html = response.read()

    soup = BeautifulSoup(html)
    
    #获取总页数
    pages = soup.find(attrs={'class':'pages'})
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
        url = "http://scbb.pkusz.edu.cn/index.php?m=content&c=index&a=lists&catid=862&page=%d" % (page + 1)
        response = urllib2.urlopen(url)
        html = response.read()

        soup = BeautifulSoup(html)

        lists = soup.find(attrs={'class':'list'})
        #print lists
        
        urls_li = lists.find_all('li')
        #print urls_li

        for url in urls_li:
            #最后一行是空行
            if url.a:
                urls.append(url.a.get('href'))
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
            article = soup.find(attrs={'class': 'main-content'})
            #print article

            title = article.h2.string
            #print title

            #string, contents
            #编码问题
            date_content = article.find(attrs={'class': 'tips'}).contents[0].encode('utf-8')
            #print date.split('\xc2\xa0\xc2')[1].split('\x9a')[1]
            date = date_content.split('\xc2\xa0\xc2')[1].split('\x9a')[1]
            #date_detail = date.split('&nbsp&nbsp&nbsp')
            #print date_detail
            
            content = article.find(attrs={'class': 'content'})
            #print content

            clicks_url = soup.find(attrs={'language':'JavaScript'})['src']
            #print clicks_url

            #获取页面点击数，通过打开js调用的连接
            response = urllib2.urlopen(clicks_url)
            clicks = response.read().split('\'')[-2]
            #print clicks

            newsItem['title'] = title.encode('utf-8')
            newsItem['date'] = date.encode('utf-8')
            newsItem['content'] = content.encode('utf-8')
            newsItem['clicks'] = clicks
            #print newsItem
            news.append(newsItem)
        #有一个页面只有一个 PDF 文件，跳过
        except AttributeError:
            pass
    #print news
    return news


def newsToMySQL(newsList):

    # 打开数据库连接
    db = MySQLdb.connect("localhost","root","","opensns", charset = 'utf8')

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    sql_checkDate = "select create_time from news where category=4 order by create_time desc limit 1"
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
        timeArray = time.strptime(a, "%Y-%m-%d %H:%M:%S")
        #转换为时间戳
        timeStamp = int(time.mktime(timeArray))

        if (timeStamp > latest_date):

            sql = "INSERT INTO news(uid, title, category, status, view, dead_line, create_time) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % ('1', item['title'], '4', '1', item['clicks'] ,'2147483640', timeStamp)
            
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
