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
    url = "http://urban.pkusz.edu.cn/index.php?m=content&c=index&a=lists&catid=747"
    response = urllib2.urlopen(url)
    html = response.read()

    soup = BeautifulSoup(html)
    #print soup
    
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
        url = "http://urban.pkusz.edu.cn/index.php?m=content&c=index&a=lists&catid=747&page=%d" % (page + 1)
        response = urllib2.urlopen(url)
        html = response.read()

        soup = BeautifulSoup(html)

        lists = soup.find(attrs={'class':'cat-list'})
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
            article = soup.find(attrs={'class': 'com-left'})
            #print article

            title = article.h2.string
            #print title
            
            #string, contents
            #编码问题
            date = article.find(attrs={'class': 'tips'}).contents[0].split('|')[0]
            #print date

            content = article.find(attrs={'class': 'content'})
            #print content

            #找到获取点击率的js链接
            try:
                clicks_url = soup.find(attrs={'class':'footer'}).find_previous_sibling().find_previous_sibling()['src']
                #print clicks_url
            except KeyError:
                pass
            response = urllib2.urlopen('http://urban.pkusz.edu.cn/' + clicks_url)
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

    sql_checkDate = "select create_time from news where category=6 order by create_time desc limit 1"
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
        
        #将datetime转换为时间戳，原字符串后有空格，此处去掉
        a = item['date'].split(' ')[0]
        b = item['date'].split(' ')[1]
        date_trans = a + ' ' + b
        #print date_trans
        #将其转换为时间数组
        timeArray = time.strptime(date_trans, "%Y-%m-%d %H:%M:%S")
        #转换为时间戳
        #print timeArray
        timeStamp = int(time.mktime(timeArray))
        #print timeStamp

        if (timeStamp > latest_date):

            sql = "INSERT INTO news(uid, title, category, status, view, dead_line, create_time) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % ('1', item['title'], '6', '1', item['clicks'] ,'2147483640', timeStamp)
            
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
    #urls = ['http://urban.pkusz.edu.cn/index.php?m=content&c=index&a=show&catid=747&id=2574']
    #print len(urls)
    news = parseNews(urls)
    #print news
    newsToMySQL(news)