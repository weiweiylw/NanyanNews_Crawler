# encoding: UTF-8

import urllib, urllib2
import cookielib

from bs4 import BeautifulSoup
import bs4

import MySQLdb
import MySQLdb.cursors

import chardet

import time

import re

import sys
reload(sys)
sys.setdefaultencoding('utf8')

def getPageCount():
    '''
    url = "http://see.pkusz.edu.cn/news_cn.aspx"
    response = urllib2.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html)
    print soup

    '''

    cj = cookielib.LWPCookieJar()
    cookie_support = urllib2.HTTPCookieProcessor(cj)
    opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
    urllib2.install_opener(opener)
    response = urllib2.urlopen('http://see.pkusz.edu.cn/news_cn.aspx')
    html = response.read()
    soup = BeautifulSoup(html)

    #获取页码
    page = soup.find(attrs={'id': 'ctl00_ContentPlaceHolder1_LinkButtonPrev'}).find_parent().contents[4].encode('utf-8').split('/')[1]
    #print filter(str.isalnum, page)
    pageCount = filter(str.isalnum, page)
    #print pageCount
    return pageCount

def getFirstPageUrls():

    urls1 = []

    cj = cookielib.LWPCookieJar()
    cookie_support = urllib2.HTTPCookieProcessor(cj)
    opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
    urllib2.install_opener(opener)
    response = urllib2.urlopen('http://see.pkusz.edu.cn/news_cn.aspx')
    html = response.read()
    soup = BeautifulSoup(html)
    url_list = soup.html.body.form.table.tbody
    #print url_list.contents

    url_list_noSpace = []
    for url in url_list:
        if (url != '\n'):
            url_list_noSpace.append(url)

    #print url_list_noSpace
    #每一个tr的间隔
    
    for i in range(0, (len(url_list_noSpace) - 3) / 2):
        #print url_list_noSpace[2 * i].contents[3].a['href']
        url = url_list_noSpace[2 * i].contents[3].a['href']
        urls1.append(url)
    #print urls1
    return urls1
    
    '''
    for tr in url_list:
        #print type(tr)
        #if isinstance(tr, bs4.element.Tag):
        #   print tr
        print tr
    '''

#使用堆上的匿名参数（函数默认值）来实现函数静态变量的功能
def getNewsUrls(pageCount, viewState_p, eventValidation_p, urls = []):
    
    if pageCount > 1:
        headers = {
            'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36',  
            'Referer' : 'http://see.pkusz.edu.cn/news_cn.aspx'
        }

        viewState = viewState_p
        eventValidation = eventValidation_p

        data = {
            '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$LinkButtonNext',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': viewState,
            '__EVENTVALIDATION': eventValidation
        }

        postData = urllib.urlencode(data)
        request = urllib2.Request('http://see.pkusz.edu.cn/news_cn.aspx', postData, headers)
        response = urllib2.urlopen(request)
        text = response.read()
        soup = BeautifulSoup(text)
        #print soup

        url_list = soup.html.body.form.table.tbody
        #print url_list.contents

        url_list_noSpace = []
        for url in url_list:
            if (url != '\n'):
                url_list_noSpace.append(url)

        #print url_list_noSpace
        #每一个tr的间隔
        
        for i in range(0, (len(url_list_noSpace) - 3) / 2):
            #print url_list_noSpace[2 * i].contents[3].a['href']
            url = url_list_noSpace[2 * i].contents[3].a['href']
            urls.append(url)
        #print urls1
              
        '''
        page = soup.find(attrs={'id': 'ctl00_ContentPlaceHolder1_LinkButtonPrev'}).find_parent().contents[4].encode('utf-8')
        #print filter(str.isalnum, page)
        pages = filter(str.isalnum, page)
        print 'page!!!!'
        print pages
        print pageCount
        '''

        viewState = soup.find(attrs={'id': '__VIEWSTATE'})['value']
        eventValidation = soup.find(attrs={'id': '__EVENTVALIDATION'})['value'] 
        #print viewState
        #print eventValidation

        getNewsUrls(pageCount - 1, viewState, eventValidation)

        return urls  

def getNewsContent(urlList):

    news =  []

    for url in urlList:

        newsItem = {}

        url_new = 'http://see.pkusz.edu.cn/' + url
        #print url_new
        response = urllib2.urlopen(url_new)
        html = response.read()
        soup = BeautifulSoup(html)

        try:
            content_all = soup.html.body.form.table.contents[1].td.table.contents[3].tr.contents[5].table.contents[3].table
            
            title = content_all.contents[1].table.tr.contents[3].string
            #print title
            date = content_all.contents[3].td.string.split(' ')[0]
            #print date
            origin = content_all.contents[3].td.string.split(' ')[3].encode('utf-8').split('\xa0')[0]
            #print origin
            clicks = content_all.contents[3].td.string.split(' ')[4]
            #print clicks
            content = content_all.contents[7].td.encode('utf-8')

            #替换原文中的相对图片地址为绝度地址
            content_new = re.sub('/userfile', 'http://see.pkusz.edu.cn/userfile', content)
            #print content_new
            #print type(content)
        except AttributeError:
            pass

        newsItem['title'] = title.encode('utf-8')
        newsItem['date'] = date.encode('utf-8')
        newsItem['origin']  = origin
        newsItem['content'] = content_new
        newsItem['clicks'] = clicks
        #print newsItem

        news.append(newsItem)        

        #break
    return news

def newsToMySQL(newsList):

    # 打开数据库连接
    db = MySQLdb.connect("localhost","root","","opensns", charset = 'utf8')

    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    sql_checkDate = "select create_time from news where category=5 order by create_time desc limit 1"
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

            sql = "INSERT INTO news(uid, title, category, status, view, dead_line, create_time) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % ('1', item['title'], '5', '1', item['clicks'] ,'2147483640', timeStamp)
            
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

    total_url = []

    total_url = getFirstPageUrls()
    total_url.extend(getNewsUrls(int(pageCount) - 1, '/wEPDwUJNTI3NDg2Mjk1D2QWAmYPZBYCAgQPZBYKZg8VARLor7fovpPlhaXlhbPplK7or41kAgEPZBYCZg9kFgJmDxUBDOaWsOmXu+aKpeWRimQCAw8WAh4LXyFJdGVtQ291bnQCAhYEZg9kFgJmDxUDDG5ld3NfY24uYXNweBFjbGFzcz0iYnV0Y2hvb3NlIgzlrabpmaLmlrDpl7tkAgEPZBYCZg8VAw5ub3RpY2VfY24uYXNweGZjbGFzcz0iYnV0bm9jaG9vc2UiIG9ubW91c2VvdmVyPSJ0aGlzLmNsYXNzTmFtZT0nYnV0Y2hvb3NlJyIgb25tb3VzZW91dD0idGhpcy5jbGFzc05hbWU9J2J1dG5vY2hvb3NlJyIM5a2m6Zmi6YCa55+lZAIEDxUBezxhIGhyZWY9J0RlZmF1bHRfY24uYXNweCcgY2xhc3M9J3doaXRlJz7pppbpobU8L2E+Jm5ic3A7Jmd0OyZndDsmbmJzcDs8YSBocmVmPSduZXdzX2NuLmFzcHgnIGNsYXNzPSd3aGl0ZSc+5paw6Ze75oql5ZGKPC9hPmQCBQ9kFggCAQ8WAh8AAgoWFGYPZBYCZg8VAwQxNDkxTuWMl+S6rOWkp+WtpueOr+Wig+enkeWtpuS4juW3peeoi+WtpumZouimgeiMguebm+eglOeptuWRmOadpeaIkemZouWtpuacr+S6pOa1gQoyMDE1LjExLjA5ZAIBD2QWAmYPFQMEMTQ4NSfot7XooYznu7/oibLnsr7npZ7vvIzkvKDmkq3njq/kv53nkIblv7UKMjAxNS4xMC4yMmQCAg9kFgJmDxUDBDE0ODJA576O5Zu9546v5L+d5Y2P5Lya5rCU5YCZ5ouT5paw6ICFMjAxNuS4reWbveaLm+WLn+S8mumhuuWIqeS4vuWKngoyMDE1LjEwLjE1ZAIDD2QWAmYPFQMEMTQ4MDbms6LlhbDnvZflhbnlt6XkuJrlpKflrabmnaXorr/miJHpmaLov5vooYzlrabmnK/kuqTmtYEKMjAxNS4xMC4wOGQCBA9kFgJmDxUDBDE0NzdL576O5Zu95p2c5YWL5aSn5a2m5byg5Yab6ZSL5pWZ5o6I5YGa5a6i5Y2X54eV56eR56CU6K665Z2b5bm25YGa57K+5b2p6K6y5bqnCjIwMTUuMDkuMjVkAgUPZBYCZg8VAwQxNDcwKOeOr+Wig+S4juiDvea6kOWtpumZouWWnOi/jjIwMTXnuqfmlrDnlJ8KMjAxNS4wOC4yNWQCBg9kFgJmDxUDBDE0Njlv5b6u5ram54GM5rqJ5oqA5pyv5pyJ6ZmQ5YWs5Y+45LiO5oiR6Zmi562+57qm5ZCI5L2c56255Yqe4oCc5Zyf5aOk5riX5p6Q6YeN6YeR5bGe5rK755CG5ZKM5L+u5aSN56CU56m25Lit5b+D4oCdCjIwMTUuMDguMTNkAgcPZBYCZg8VAwQxNDY4LjIwMTXlhajlm73kvJjnp4DlpKflrabnlJ/lpI/ku6TokKXlnIbmu6Hnu5PmnZ8KMjAxNS4wNy4yN2QCCA9kFgJmDxUDBDE0NjdL5rex5Zyz5rW35rSL5bGA5Ya356eR5piO6auY5bel6KKr6IGY5Li65oiR6Zmi5a6i5bqn5pWZ5o6I5bm25L2c5a2m5pyv5oql5ZGKCjIwMTUuMDcuMTZkAgkPZBYCZg8VAwQxNDY2NOaIkemZouaIkOWKn+S4vuWKnjIwMTXnjq/og73lrabpmaLmr5XkuJrnlJ/kuqTmtYHkvJoKMjAxNS4wNy4xMGQCAw8PFgIeB0VuYWJsZWRoZGQCBQ8PFgIfAWhkZAIGDxUCATECNDVkZHK432brxKFI918O/cmpZssyL7zM', '/wEWAwKTz89aAoyKo8EDAof8/VbhMsk1X7LOGblMSBzg798JD4VOmQ=='))
    #print total_url
    news = getNewsContent(total_url)
    
    newsToMySQL(news)
