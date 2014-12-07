#-*- encoding: utf-8 -*-
__author__ = 'alex'

import re
import time

from scrapy.contrib.spiders import CrawlSpider
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
                yield Request(self.film_pre_url + film_id + self.film_suf_url, headers={"status": status},
                              callback=self.parse_film)
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
        information = {}

        information["name"] = sel.xpath("//h1/span[@property='v:itemreviewed']/text()").extract()[0]
        information["year"] = sel.xpath("//h1/span[@class='year']/text()").extract()[0].replace('(', '').replace(')', '')

        information["director"] = sel.xpath("//span/a[@rel='v:directedBy']/text()").extract()[0]
        information["screenwriter"] = sel.xpath("//div[@id='info']/span[2]/span[2]/a/text()").extract()
        information["starring"] = sel.xpath("//span[@class='actor']/span[2]/a/text()").extract()
        information["style"] = sel.xpath("//span[@property='v:genre']/text()").extract()

        is_rating = sel.xpath("//strong[@class='ll rating_num']/text()")
        item['rating'] = float(is_rating[0].extract()) if is_rating else None

        producedIn_reg = r'''<span class="pl">制片国家/地区:</span>(.*?)<'''
        language_reg = r'''<span class="pl">语言:</span>(.*?)<'''
        aliases_reg = r'''<span class="pl">又名:</span>(.*?)<'''
        IMDb_reg = r'''<span class="pl">IMDb链接:</span>\s*<a.*?href="(.*?)"'''
        information["producedIn"] = re.compile(producedIn_reg, re.S).search(content).group(1)
        information["language"] = re.compile(language_reg, re.S).search(content).group(1)

        aliases_res = re.compile(aliases_reg, re.S).search(content)
        if aliases_res:
            information["aliases"] = aliases_res.group(1)
        IMDb_res = re.compile(IMDb_reg, re.S).search(content)
        if IMDb_res:
            information["IMDb"] = IMDb_res.group(1)

        information["dateToRelease"] = sel.xpath("//span[@property='v:initialReleaseDate']/text()").extract()
        length_res = sel.xpath("//span[@property='v:runtime']/text()")
        if length_res:
            information["length"] = length_res.extract()[0]

        item["synopsis"] = sel.xpath("//span[@property='v:summary']/text()")[0].extract()
        item["tags"] = sel.xpath("//div[@class='tags-body']/a/text()").extract()
        item['status'] = status
        commentary_res = sel.xpath("//div[@class='comment']")

        item['commentary'] = []
        item['reviews'] = []
        for i in commentary_res:
            comment = {
                "author": i.xpath("./h3/span[2]/a/text()")[0].extract(),
                # "time_str": i.xpath("./h3/span[2]/span[2]/text()")[0].extract(),
                "content": i.xpath("./p/text()")[0].extract()
            }
            item['commentary'].append(comment)

        review_res = sel.xpath("//div[@class='review']")
        for i in review_res:
            review = {
                "author": i.xpath("./div[1]/div/a/text()")[0].extract(),
                "time_str": i.xpath("./div[1]/div/text()[2]")[0].extract(),
                "content": i.xpath("./div[2]/div/span/text()")[0].extract()
            }
            item['reviews'].append(review)

        item["info"] = information
        item['createAt'] = int(time.time() * 1000)
        return item
