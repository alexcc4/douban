#-*- encoding: utf-8 -*-
__author__ = 'alex'

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy import log
from scrapy import Selector

from douban.items import FilmItem

class FilmSpider(CrawlSpider):
    '''
    @crawl for films on douban film
    @created by alex
    @date 2014-9-17
    '''

    name = 'film'
    allowed_domains = ['movie.douban.com']
    start_urls = ['http://movie.douban.com/nowplaying/guangzhou/']
    rules = (
        Rule(LinkExtractor(allow=('\/subject\/\d+\/',)), callback='parse_film'),
    )

    def parse_film(self, response):
        '''
        @parse the film item from the page
        '''
        log.msg(response.url + '~~~~~~~~~~~~~~~~~~~~~~')
        sel = Selector(response)
        item = FilmItem()
        name = sel.xpath("//h1/span[@property='v:itemreviewed']/text()").extract()
        year = sel.xpath("//h1/span[@class='year']/text()").extract()

        info = sel.xpath("//div[@id='info']")
        director = info.xpath("//span/a[@rel='v:directedBy']/text()").extract()
        screenwriter = sel.xpath("//div[@id='info']/span[2]/a/text()").extract()
        starring = sel.xpath("//div[@id='info']/span[2]/a/text()").extract()
        style = info.xpath("//span[@property='v:genre']/text()").extract()
        producedIn = info.xpath("//span[@property='v:genre']/text()").extract()
        
