# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo

from scrapy.conf import settings
from scrapy.exceptions import DropItem
from souq.items import create_index


class SouqPipeline(object):
    def __init__(self):
        connection = pymongo.MongoClient(settings['MONGODB_URI'])
        self.db = connection[settings['MONGODB_DB']]

    def open_spider(self, spider):
        create_index(self.db)

    def process_item(self, item, spider):
        dict_item = item.to_dict()
        try:
            # try to use orm for mongo
            self.db[item.collection_name].insert(dict_item)
        except:
            pass
        # spider.logger.info("Save the item into DB. Detail-{}".format(dict(item)))
        return item
