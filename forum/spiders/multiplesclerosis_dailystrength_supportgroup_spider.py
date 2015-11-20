import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.selector import Selector
from forum.items import PostItemsList
import re
import logging
from bs4 import BeautifulSoup
# import lxml.html
# from lxml.etree import ParserError
# from lxml.cssselect import CSSSelector

## LOGGING to file
#import logging
#from scrapy.log import ScrapyFileLogObserver

#logfile = open('testlog.log', 'w')
#log_observer = ScrapyFileLogObserver(logfile, level=logging.DEBUG)
#log_observer.start()

# Spider for crawling Adidas website for shoes
class ForumsSpider(CrawlSpider):
    name = "multiplesclerosis_dailystrength_supportgroup_spider"
    allowed_domains = ["dailystrength.org"]
#    start_urls = [
#        "http://www.healingwell.com/community/default.aspx?f=23&m=1001057",
#    ]
    start_urls = [
        "http://www.dailystrength.org/c/Renal-Cell-Carcinoma-Kidney-Cancer/support-group",
    ]

    rules = (
            # Rule to go to the single product pages and run the parsing function
            # Excludes links that end in _W.html or _M.html, because they point to 
            # configuration pages that aren't scrapeable (and are mostly redundant anyway)
            Rule(LinkExtractor(
                restrict_xpaths='//table[contains(@class, "topic_snip")]',
                canonicalize=True,
                deny='http://www.dailystrength.org/people/',
                ), callback='parsePost'),

            # Rule(LinkExtractor(
            #     restrict_xpaths='//*[@id="col1"]/div[2]/div[2]/div[1]/table/tr[3]/td[1]/a[1]/@href',
            # ), follow=True),
        )

    def cleanText(self,text):
        soup = BeautifulSoup(text,'html.parser')
        text = soup.get_text();
        text = re.sub("( +|\n|\r|\t|\0|\x0b|\xa0|\xbb|\xab)+",' ',text).strip()
        return text 


    # https://github.com/scrapy/dirbot/blob/master/dirbot/spiders/dmoz.py
    # https://github.com/scrapy/dirbot/blob/master/dirbot/pipelines.py
    def parsePost(self,response):
        logging.info(response)
        sel = Selector(response)
        posts = sel.xpath('//*[@id="col1"]/div[2]/div[2]/div[1]/table[4]')
        items = []
        condition="multiple sclerosis"
        topic = sel.xpath('//div[contains(@class, "discussion_topic_header_subject")]/text()').extract()[0]
        url = response.url
        post = sel.xpath('//table[contains(@class, "discussion_topic")]')
        item = PostItemsList()
        item['author'] = post.css('.username').xpath("./a").xpath("text()").extract()[0].strip()
        item['author_link']=response.urljoin(post.css('.username').xpath("./a/@href").extract()[0])
        item['condition']=condition
        item['create_date']= re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',post.css('.discussion_text').xpath('./span/text()').extract()[0]).strip()
        item['post']=self.cleanText(post.css('.discussion_text').extract()[0])
        # item['tag']='epilepsy'
        item['topic'] = topic
        item['url']=url
        items.append(item)

        for post in posts:
            item = PostItemsList()
            if len(post.css('.username')) == 0:
                continue
            item['author'] = post.css('.username').xpath("./a").xpath("text()").extract()[0].strip()
            item['author_link']=response.urljoin(post.css('.username').xpath("./a/@href").extract()[0])
            item['condition'] = condition
            item['create_date']= re.sub(" +|\n|\r|\t|\0|\x0b|\xa0",' ',post.xpath('./tr[1]/td[2]/div/table/tr/td/span[2]/text()').extract()[0]).strip()
            item['post']=self.cleanText(post.css('.discussion_text').extract()[0])
            # item['tag']=''
            item['topic'] = topic
            item['url']=url
            items.append(item)
        return items
