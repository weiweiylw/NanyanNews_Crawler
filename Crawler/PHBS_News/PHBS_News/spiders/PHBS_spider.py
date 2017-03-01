# encoding: UTF-8
# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

import scrapy
import re

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from PHBS_News.items import PhbsNewsItem

from bs4 import BeautifulSoup

import urllib2

import sys
reload(sys)
sys.setdefaultencoding('utf8')

class PhbsNewsSpider(CrawlSpider):
    name = 'PhbsNews'
    allowed_domains = ['www.phbs.pku.edu.cn']
    start_urls = ['http://www.phbs.pku.edu.cn/list-419-1.html']

    rules = [Rule(SgmlLinkExtractor(allow=['http://www.phbs.pku.edu.cn/list-419-\d*.html'])),
             Rule(SgmlLinkExtractor(allow=['http://www.phbs.pku.edu.cn/content-419']), 'parse_torrent')]

    def parse_torrent(self, response):
        soup = BeautifulSoup(response.body)
        #print soup

        title = soup.find(attrs={'class':'title'}).string
        #print title

        date = soup.find(attrs={'class':'inputtime'}).string
        #print date

        orgin = soup.find(attrs={'class':'username'}).string
        #print orgin

        clicks_url = soup.find(attrs={'language':'JavaScript'})['src']
        #print clicks_url

		#获取页面点击数，通过打开js调用的连接
        response = urllib2.urlopen(clicks_url)
        clicks = response.read().split('\'')[-2]
        #print clicks

        content = soup.find(attrs={'class':'content'})
        #print content

        #建立数据库时指定编码为utf-8，此处需统一编码

        items = PhbsNewsItem()
        items['title'] = title.encode('utf-8')
        items['date'] = date
        items['origin'] = orgin
        items['clicks'] = clicks
        items['content'] = content

        #print items

        return items