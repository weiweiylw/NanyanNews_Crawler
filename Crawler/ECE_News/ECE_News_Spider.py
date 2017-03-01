# encoding: UTF-8

import urllib2
from bs4 import BeautifulSoup

import MySQLdb
import MySQLdb.cursors

import chardet

def getPageCount():
    url = "http://www.ece.pku.edu.cn/index.php?m=content&c=index&a=lists&catid=502"
    response = urllib2.urlopen(url)
    html = response.read()

    soup = BeautifulSoup(html)
    
    #获取总页数
    pages = soup.find(attrs={'class':'pages'})
    page = pages.find_all('a')
    
    #倒数第二个元素
    pageCount = int(page[-2].string)
    
    return pageCount

def getNewsUrls(pageCount):

    #print type(pageCount)
    urls = []
    
    for page in range(pageCount):
        #print type(page)
        url = "http://www.ece.pku.edu.cn/index.php?m=content&c=index&a=lists&catid=502&page=%d" % (page + 1)
        response = urllib2.urlopen(url)
        html = response.read()

        soup = BeautifulSoup(html)

        lists = soup.find(attrs={'class':'lists'})
        #print lists
        
        urls_li = lists.find_all('li')
        #print urls
        
        for url in urls_li:
            urls.append(url.a.get('href'))

    return urls

def parseNews(urlList):
    news = []
    
    for url in urlList:
        try:
            newsItem = {}
            
            response = urllib2.urlopen(url)
            html = response.read()

            soup = BeautifulSoup(html)
            article = soup.find(attrs={'class': 'article'})
            
            title = article.h1.string
            
            date = article.find(attrs={'class': 'tips'}).string
            #print date
            
            content = article.find(attrs={'class': 'content'})
            #print content
            
            newsItem['title'] = title.encode('utf-8')
            newsItem['date'] = date.encode('utf-8')
            newsItem['content'] = content.encode('utf-8')
            #print newsItem
            news.append(newsItem)
        #有一个页面只有一个 PDF 文件，跳过
        except AttributeError:
            pass

    return news

def newsToMySQL(newsList):

    # 打开数据库连接
    db = MySQLdb.connect("localhost","root","","opensns2", charset = 'utf8')

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    for item in newsList:
        #print item['content'].encode('gbk')
        #print '\n'
        #print chardet.detect(item['content'])
        '''
        print type(item['date'])
        print type(item['content'])
        print '\n'
        '''
        
        sql = "INSERT INTO ece_news(title, date, content) VALUES ('%s', '%s', '%s')" % (item['title'], item['date'], item['content'])

        try:
           # 执行sql语句
           cursor.execute(sql)
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