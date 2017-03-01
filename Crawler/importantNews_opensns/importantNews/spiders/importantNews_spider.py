# encoding: UTF-8
# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

import scrapy
import re

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from importantNews.items import ImportantnewsItem

from bs4 import BeautifulSoup

import urllib2

class importantNewsSpider(CrawlSpider):
    name = 'importantNews'
    allowed_domains = ['news.pkusz.edu.cn']
    start_urls = ['http://news.pkusz.edu.cn/']

    rules = [Rule(SgmlLinkExtractor(allow=['http://news.pkusz.edu.cn/list-143-\d*.html'])),
             Rule(SgmlLinkExtractor(allow=['http://news.pkusz.edu.cn/article-143']), 'parse_torrent')]
    
    def parse_torrent(self, response):
        soup = BeautifulSoup(response.body)
        #print soup

        title = soup.find(attrs={'class':'titlelb2'}).string
        #print title

        date = soup.find(attrs={'class':'rightnew con_6 fr'}).contents[5].contents
        #xc2\xa0为空格，\xef\xbc\x9a为冒号
        date_new = date[0].encode('utf-8').split('\xc2\xa0\xc2\xa0\xc2\xa0')[0].split('\xef\xbc\x9a')[1]
        #print date_new

        orgin = date[0].encode('utf-8').split('\xc2\xa0\xc2\xa0\xc2\xa0')[1].split('：')[1]
        #print orgin

        comments = soup.find(attrs={'id':'comment'}).string
        #print comments

        #为何clicks获取不到？
        #clicks = soup.find(attrs={'id':'hits'})
        #clicks = soup.find(attrs={'class':'rightnew con_6 fr'}).contents[6]
        #print clicks

        clicks_url = soup.find(attrs={'language':'JavaScript'})['src']
        #print clicks_url

        #获取页面点击数，通过打开js调用的连接
        response = urllib2.urlopen(clicks_url)
        clicks = response.read().split('\'')[-2]
        #print clicks        

        content = soup.find(attrs={'id':'content'})

        #建立数据库时指定编码为utf-8，此处需统一编码

        items = ImportantnewsItem()
        items['title'] = title.encode('utf-8')
        items['date'] = date_new
        items['origin'] = orgin
        items['comments'] = comments.encode('utf-8')
        items['clicks'] = clicks
        items['content'] = content

        #print items

        return items