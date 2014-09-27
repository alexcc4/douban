#-*- encoding: utf-8 -*-
__author__ = 'alex'

import re

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy import log
from scrapy import Selector
from scrapy import Request

from douban.items import FilmItem

class FilmSpider(CrawlSpider):
    '''
    @crawl for films on douban film
    @created by alex
    @date 2014-9-17
    '''

    name = 'film'
    allowed_domains = ['movie.douban.com']
    start_urls = [
        'http://movie.douban.com/nowplaying/guangzhou/',
        'http://movie.douban.com/later/guangzhou/'
        ]
    # rules = (
    #     Rule(LinkExtractor(allow=('\/subject\/\d+\/',)), callback='parse_film'),
    # )
    film_pre_url = 'http://movie.douban.com/subject/'
    film_suf_url = '/?from=playing_poster'

    def parse(self, response):
        '''
        @parse the nowplaying film id and coming film id
        '''

        status = response.url.split('/')[3]
        if status == 'nowplaying':
            ids = Selector(response).xpath("//div[@class='mod-bd']/ul/li/@id").extract()
            for film_id in ids:
                yield Request(self.film_pre_url + film_id + self.film_suf_url, headers={"status": status}, callback=self.parse_film)
        else:
            urls = Selector(response).xpath("//a[@class='thumb']/@href").extract()
            for film_url in urls:
                yield Request(film_url, headers={"status": status}, callback=self.parse_film)

    def parse_film(self, response):
        '''
        @parse the film item from the page
        '''
        status = response.request.headers["status"]

        sel = Selector(response)
        content = response.body

        item = FilmItem()
        infomation = {}

        infomation["name"] = sel.xpath("//h1/span[@property='v:itemreviewed']/text()").extract()[0]
        infomation["year"] = sel.xpath("//h1/span[@class='year']/text()").extract()[0].replace('(', '').replace(')', '')

        info = sel.xpath("//div[@id='info']")
        infomation["director"] = info.xpath("//span/a[@rel='v:directedBy']/text()").extract()[0]
        infomation["screenwriter"] = sel.xpath("//div[@id='info']/span[2]/a/text()").extract()
        infomation["starring"] = sel.xpath("//div[@id='info']/span[2]/a/text()").extract()
        infomation["style"] = info.xpath("//span[@property='v:genre']/text()").extract()

        producedIn_reg = r'''<span class="pl">制片国家/地区:</span>(.*?)<'''
        language_reg = r'''<span class="pl">语言:</span>(.*?)<'''
        aliases_reg = r'''<span class="pl">又名:</span>(.*?)<'''
        IMDb_reg = r'''<span class="pl">IMDb链接:</span>\s*<a.*?href="(.*?)"'''
        infomation["producedIn"] = re.compile(producedIn_reg, re.S).search(content).group(1).decode('utf-8')
        infomation["language"] = re.compile(language_reg, re.S).search(content).group(1).decode('utf-8')

        aliases_res = re.compile(aliases_reg, re.S).search(content)
        if aliases_res:
            infomation["aliases"] = aliases_res.group(1).decode('utf-8')
        IMDb_res = re.compile(IMDb_reg, re.S).search(content)
        if IMDb_res:
            infomation["IMDb"] = IMDb_res.group(1)

        infomation["dateToRelease"] = info.xpath("//span[@property='v:initialReleaseDate']/text()").extract()
        length_res = info.xpath("//span[@property='v:runtime']/text()")
        if length_res:
            infomation["length"] = length_res.extract()[0]
        #TODO decode('utf-8')?
        item["synopsis"] = sel.xpath("//span[@property='v:summary']/text()")[0].extract().decode('utf-8')
        item["tags"] = sel.xpath("//div[@class='tags-body']/a/text()").extract()

        commentary_res = sel.xpath("//div[@class='comment']/p/text()").extract()
        if commentary_res:
            item["commentary"] = commentary_res
        review_res = sel.xpath("//div[@class='review-bd']/div/span/text()").extract()
        if review_res:
            item["reviews"] = review_res

        item["info"] = infomation
        log.msg(item["tags"][0].decode('utf-8') + '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

