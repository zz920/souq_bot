# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import pymongo
import scrapy


class MongoItemMixIn:
    def to_dict(self):
        return dict(self)


class CategoryItem(scrapy.Item, MongoItemMixIn):
    # define the fields for your item here like:
    # name = scrapy.Field()
    parent = scrapy.Field()
    name = scrapy.Field()
    link = scrapy.Field()

    collection_name = "Category"


class SouqItem(scrapy.Item, MongoItemMixIn):
    name = scrapy.Field()
    category = scrapy.Field()
    link = scrapy.Field()
    price = scrapy.Field()
    trace_id = scrapy.Field()

    seller = scrapy.Field()
    seller_link = scrapy.Field()
    quantity = scrapy.Field()
    description = scrapy.Field()
    create_at = scrapy.Field()
    # update_at = scrapy.Field()

    collection_name = "Souqitem"

    def to_dict(self):
        data = super(SouqItem, self).to_dict()
        try:
            data['price'] = float(data['price'])
        except:
            pass

        try:
            data['quantity'] = int(data['quantity'])
        except:
            pass
        return data


def create_index(db):
    db[CategoryItem.collection_name].create_index(
        [("link", pymongo.DESCENDING)],
    )
    db[SouqItem.collection_name].create_index(
        [("link", pymongo.DESCENDING)],
    )
    db[SouqItem.collection_name].create_index(
        [("seller", pymongo.DESCENDING)],
    )
    db[SouqItem.collection_name].create_index(
        [("trace_id", pymongo.DESCENDING)],
    )
    db[SouqItem.collection_name].create_index(
        [("create_at", pymongo.DESCENDING)],
    )
