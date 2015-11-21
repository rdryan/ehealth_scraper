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

# Spider for crawling Adidas website for shoes
class ForumsSpider(CrawlSpider):
    name = "lungcancer_cancerforums_spider"
    allowed_domains = ["www.cancerforums.net"]
    start_urls = [
        "http://www.cancerforums.net/forums/13-Lung-Cancer-Forum",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//h3/a[@class="title"]',
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//span[@class="prev_next"]/a[@rel="next"]'
                ), follow=True),
        )

    def cleanText(self, str):
        soup = BeautifulSoup(str, 'html.parser')
        return re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',soup.get_text()).strip()


    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePostsList(self,response):
        sel = Selector(response)
        posts = sel.xpath('//ol[@class="posts"]/li[@class="postbitlegacy postbitim postcontainer old"]')
        condition = "lung cancer"
        items = []
        topic = response.xpath('//h1/span[@class="threadtitle"]/a/text()').extract_first()
        url = response.url
        
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//div[@class="popupmenu memberaction"]/a/strong/text()').extract_first()
            item['author_link'] = post.xpath('.//div[@class="popupmenu memberaction"]/a/@href').extract_first()
            item['condition'] = condition
            item['create_date'] = post.xpath('.//span[@class="date"]/text()').extract_first().replace(',','').strip()
            item['post'] = re.sub(r'\s+',' ',self.cleanText(" ".join(post.xpath('.//div[@class="content"]//blockquote/text()').extract())))
            # item['tag']=''
            item['topic'] = topic
            item['url']=url
            items.append(item)
        return items
