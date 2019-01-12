import os
import re
import traceback
import scrapy
from datetime import datetime

from souq.items import CategoryItem, SouqItem
from scrapy_redis.spiders import RedisSpider


log_indent = lambda t, s: t * 20 + s + t *20
_to_url = lambda url: url if url.startswith("https://uae.souq.com") else "https://uae.souq.com" + url


class SellerSpider(RedisSpider):
    name = "sellers"

    """
    start_urls = [
        'https://uae.souq.com/ae-en/shop-all-categories/c'
    ]
    """

    def parse(self, response):
        self.logger.debug(log_indent("=", "Finish Crawling the Index Page, Try to analyze detail page..."))
        main_block = response.xpath("//main[@class='main-section ']")[0]
        url_pool = []
        for block in main_block.xpath("div//div[@class='large-4 columns']"):
            shop_category = block.xpath("h3/text()").extract()
            group_category = block.xpath("div[@class='grouped-list']")
            self.logger.debug("Total group numbers: {}".format(len(group_category)))
            for shop_title, group_block in zip(shop_category, group_category):
                self.logger.debug("Extracting {} category...".format(shop_title))
                for group_a in group_block.xpath("ul//li[not(@class)]/a"):
                    group_link = group_a.xpath("@href").extract_first()
                    group_name = group_a.xpath("text()").extract_first()
                    yield CategoryItem(parent=shop_title, name=group_name, link=group_link)
                    url_pool.append(group_link)

        self.logger.debug(log_indent("=", "Start Analyzing the item pages..."))
        for link in url_pool:
            start_page = "{}?ref=nav&section=2&page=1".format(link)
            request = scrapy.Request(url=_to_url(start_page), callback=self.parse_item_page)
            request.meta['ini_url'] = start_page
            yield request

    def parse_item_page(self, response):
        self.logger.debug(log_indent("-", "Handling item page of {}".format(response.meta['ini_url'])))
        ini_url = response.meta['ini_url']

        if ini_url != response.url:
            # the page is redirected
            self.logger.error("Page is being redirected: {}".format(ini_url))
            return

        request_list = []
        item_block = response.xpath("//div[@class='column column-block block-grid-large single-item']")
        # page_num = re.findall("page=[0-9]*", response.url)[0].split("=")[-1]
        for item in item_block:
            item_link = item.xpath("div//a[@class='img-link quickViewAction sPrimaryLink']/@href").extract_first()
            if item_link:
                request_list.append(scrapy.Request(url=_to_url(item_link), callback=self.parse_detail))

        self.logger.info("[{}] Total {} items for page {}".format(os.getpid(), len(request_list), ini_url))
        # enqueue requests
        for request in request_list:
            yield request

        next_page = response.xpath("//li[@class='pagination-next goToPage']/a/@href").extract_first()

        if next_page is None:
            self.logger.info("[{}] Page end at {}".format(os.getpid(), ini_url))
            return


        request = scrapy.Request(url=_to_url(next_page + "&section=2"), callback=self.parse_item_page)
        request.meta['ini_url'] = next_page + "&section=2"
        yield request

    def parse_detail(self, response):
        try:
            product_title_block = response.xpath("//div[@class='small-12 columns product-title']")

            name = product_title_block.xpath("h1/text()").extract_first()
            if name is None:
                # invalid item
                return
            category = product_title_block.xpath("span/a[2]/text()").extract_first()
            self.logger.debug(log_indent(".", "Handle {}".format(name)))
            link = response.url

            trace_id = link.split("/")[4].split("-")[-1]

            price_block = response.xpath("//section[@class='price-messaging']/div//h3[@class='price is sk-clr1']")
            raw_price = price_block.xpath("text()[2]").extract_first()
            if raw_price is None:
                # sold out in this case
                price = -1
            else:
                price = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", raw_price)[0]

            description = "\n".join(response.xpath("//div[@class='item-details-mini clearfix']/ul/li/text()").extract())

            seller_block = response.xpath("//span[@class='unit-seller-link']/a")

            # check is amazon global
            if not seller_block:
                seller = "Amazon Global"
                seller_link = ""
            else:
                seller = seller_block.xpath("b/text()").extract_first()
                seller_link = seller_block.xpath("@href").extract_first()
                if not seller_link:
                    raise Exception("Empty seller link.")

            create_at = datetime.isoformat(datetime.now())
            # update_at = datetime.datetime.now()

            # quantity
            match = re.search('"quantity":(?P<quantity>[0-9]+)', response.body.decode('utf-8', 'ignore'))
            if match:
                quantity = match.group('quantity')
            else:
                raise Exception("Souq page changed the logic.")
            # self.logger.debug("::::Fetchr item {} - {} AED::::".format(name[10:], price))
            yield SouqItem(name=name, category=category, link=link, price=price, trace_id=trace_id,
                           seller=seller, seller_link=seller_link, quantity=quantity,
                           description=description, create_at=create_at)
        except Exception:
            self.logger.error("Exception {}, try {} manually".format(traceback.format_exc(), link))
