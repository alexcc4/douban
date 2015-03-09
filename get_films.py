#-*- encoding: utf-8 -*-
__author__ = 'alex'

from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy import log, signals
from scrapy.utils.project import get_project_settings
from douban.spiders.filmSpider import FilmSpider

settings = get_project_settings()
crawler = Crawler(settings)
crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
crawler.configure()
crawler.crawl(FilmSpider())
crawler.start()
log.start()
reactor.run()




