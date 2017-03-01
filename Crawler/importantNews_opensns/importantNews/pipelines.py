# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

#import json
#import codecs

import MySQLdb
import MySQLdb.cursors

from twisted.enterprise import adbapi

from scrapy import log

import time

import sys
reload(sys)
sys.setdefaultencoding('utf8')

#数据库保存
class MySQLStorePipeline(object):
    #init只执行一次
    def __init__(self):

        self.db = MySQLdb.connect("localhost","root","","opensns", charset = 'utf8')
        self.cursor = self.db.cursor()

        sql_checkDate = "select create_time from news where category=1 order by create_time desc limit 1"
        self.cursor.execute(sql_checkDate)
        result = self.cursor.fetchall()
        if (result):
            self.latest_date = result[0][0]
        else:
            self.latest_date = 0

    #pipeline默认调用
    def process_item(self, item, spider):

        #将datetime转换为时间戳：
        a = item['date'];
        #将其转换为时间数组
        timeArray = time.strptime(a, "%Y-%m-%d %H:%M:%S")
        #转换为时间戳
        timeStamp = int(time.mktime(timeArray))

        '''
        print 'latest!!!!'
        print timeStamp
        print self.latest_date
        '''

        if (timeStamp > self.latest_date):

            sql = "INSERT INTO news(uid, title, category, status, view, dead_line, create_time) VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % ('1', item['title'], '1', '1', item['clicks'], '2147483640', timeStamp)

            try:
               # 执行sql语句
               self.cursor.execute(sql)
               #print "ID of last record is ", int(cursor.lastrowid) #最后插入行的主键ID  
               sql_detail = "INSERT INTO news_detail(news_id, content) VALUES (%d, '%s')" % (int(self.cursor.lastrowid), item['content'])
               self.cursor.execute(sql_detail)

               # 提交到数据库执行
               self.db.commit()
            except:
               # Rollback in case there is any error
               self.db.rollback()

        return item

    def handle_error(self, e):
        log.err(e)

