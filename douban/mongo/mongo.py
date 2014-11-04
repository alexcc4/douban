#-*- encoding: utf-8 -*-
__author__ = 'alex'

from pymongo import MongoClient
from scrapy.utils.project import get_project_settings
from scrapy import log

settings = get_project_settings()

def mongoCon():
    try:
        mongo = MongoClient(settings.get('DB_HOST'), settings.get('DB_PORT'))
        return mongo
    except Exception, e:
        log.msg('connect mongo error:' + repr(e))
        return None




