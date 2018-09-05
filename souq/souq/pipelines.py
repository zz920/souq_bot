# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo

from scrapy.conf import settings
from scrapy.exceptions import DropItem
from souq.items import CategoryItem


class SouqPipeline(object):
    def __init__(self):
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = connection[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]

    def process_item(self, item, spider):
        for data in item:
            if not data:
                raise DropItem("Missing {}!".format(data))
        self.collection.insert(dict(item))
        # spider.logger.info("Save the item into DB. Detail-{}".format(dict(item)))
        return item
