#!/bin/bash
service mongod restart
scrapy crawl sellers --loglevel INFO --logfile /var/log/souqbot.log
