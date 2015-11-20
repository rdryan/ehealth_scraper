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

class ForumsSpider(CrawlSpider):
    name = "hepc_healingwell_spider"
    allowed_domains = ["www.healingwell.com"]
    start_urls = [
        "http://www.healingwell.com/community/default.aspx?f=25",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                    restrict_xpaths='//td[@class="msgTopicAnnounce TopicTitle"]/a', 
                ), callback='parsePostsList'),
            # Rule to follow arrow to next product grid
            Rule(LinkExtractor(
                    restrict_xpaths='//td[@class="msgSm" and @align="right"]/b/strong/following-sibling::a[1]'
                ), follow=True),
        )

    def cleanText(self,text):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        return text 

    def parsePostsList(self,response):
        sel = Selector(response)
        posts = sel.xpath('//table[@class="PostBox"]')
        items = []
        topic = response.xpath('//h1/text()').extract_first()
        url = response.url
        condition="hep c"
        for post in posts:
            item = PostItemsList()
            item['author'] = post.xpath('.//td[@class="msgUser"]/a[2]/text()').extract_first()
            if item['author']:
                item['author_link'] = post.xpath('.//td[@class="msgUser"]/a[2]/@href').extract_first()
                item['condition'] = condition
                item['create_date'] = post.xpath('.//td[@class="msgThreadInfo PostThreadInfo"]/text()').extract_first().replace(u'\xa0','').replace(u'Posted','').strip()
                item['post'] = self.cleanText(" ".join(post.xpath('.//div[@class="PostMessageBody"]/text()').extract()))
                # item['tag']='epilepsy'
                item['topic'] = topic.strip()
                item['url']=url
                logging.info(item.__str__)
                items.append(item)
        return items
