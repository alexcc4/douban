# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class FilmItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
    info = Field()
    synopsis = Field()
    tags = Field()
    commentary = Field()
    reviews = Field()
    status = Field()
    createAt = Field()
