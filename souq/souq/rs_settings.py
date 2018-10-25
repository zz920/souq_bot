# -*- coding: utf-8 -*-
import os
# Scrapy settings for souq project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'souq'

SPIDER_MODULES = ['souq.spiders']
NEWSPIDER_MODULE = 'souq.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# DB settings
MONGODB_SERVER = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017')
MONGODB_DB = "souq"

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 4

# Redis Scrapy Settings
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"

ITEM_PIPELINES = {
    'scrapy_redis.pipelines.RedisPipeline': 300,
    'souq.pipelines.SouqPipeline': 301,
}

REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')
REDIS_STRAT_URLS_KEY = "sellers:start_urls https://uae.souq.com/ae-en/shop-all-categories/c"

RETRY_ENABLED = True
DOWNLOAD_TIMEOUT = 15
REDIRECT_ENABLED = True
