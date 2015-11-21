# -*- coding: utf-8 -*-
import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
import re
from bs4 import BeautifulSoup
import logging
import string

## LOGGING to file
#import logging
#from scrapy.log import ScrapyFileLogObserver

#logfile = open('testlog.log', 'w')
#log_observer = ScrapyFileLogObserver(logfile, level=logging.DEBUG)
#log_observer.start()

# Spider for crawling Adidas website for shoes
class ForumsSpider(CrawlSpider):
    name = "epilepsy_epilepsysociety_spider"
    allowed_domains = ["forum.epilepsysociety.org.uk"]
    start_urls = [
        "http://forum.epilepsysociety.org.uk/viewforum.php?f=3&sid=f42f2143fd39c59e3618c210d49c574c",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//a[@class="topictitle"]',
                    canonicalize=True,
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//tr/td/b/a[last()]',
                    canonicalize=True,
                ), follow=True),
        )

    def cleanText(self,text):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        return text 

    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePostsList(self,response):
        sel = Selector(response)
        posts = sel.xpath('//table[@class="tablebg "]')
        items = []
        condition="epilepsy"
        topic = response.xpath('//h2/a[@class="titles"]/text()').extract_first()
        url = response.url
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//b[@class="postauthor"]/text()').extract_first()
            item['author_link']=post.xpath('.//div[@class="gensmall" and @style="float: left;"]/a/@href').extract_first()
            item['condition']=condition
            item['create_date'] = post.xpath('.//td[@class="gensmall" and @width="100%"]/div[@style="float: right;"]/text()').extract_first().strip()

            message = " ".join(post.xpath('.//div[@class="postbody"]/text()').extract())
            item['post'] = self.cleanText(message)

            # item['post'] = re.sub('\s+',' '," ".join(post.xpath('.//div[@class="postbody"]/text()').extract()).replace("\t","").replace("\n","").replace("\r",""))

            # item['tag']=''
            item['topic'] = topic
            item['url']=url
            items.append(item)
        return items
