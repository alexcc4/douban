# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
#TODO to parse str to timestamp
from douban.mongo.mongo import mongoCon


class DoubanPipeline(object):

    def __init__(self):
        self.mongo = mongoCon()

    def process_item(self, item, spider):

        if self.mongo:
            films = self.mongo.douban.films
            information = item['info']
            films.update({"name": information['name'], "year": information['year']}, dict(item), True)
