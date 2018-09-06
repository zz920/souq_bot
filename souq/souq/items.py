# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import pymongo
import scrapy


class CategoryItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    parent = scrapy.Field()
    name = scrapy.Field()
    link = scrapy.Field()

    collection_name = "Category"


class SouqItem(scrapy.Item):
    name = scrapy.Field()
    category = scrapy.Field()
    link = scrapy.Field()
    price = scrapy.Field()
    seller = scrapy.Field()
    seller_link = scrapy.Field()
    description = scrapy.Field()
    update_at = scrapy.Field()

    collection_name = "Souqitem"


def create_index(db):
    db[CategoryItem.collection_name].create_index(
        [("link", pymongo.DESCENDING)],
        unique=True
    )
    db[SouqItem.collection_name].create_index(
        [("link", pymongo.DESCENDING)],
        unique=True
    )
