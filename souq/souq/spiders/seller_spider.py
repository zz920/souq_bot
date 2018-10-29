import re
import scrapy
import datetime

from souq.items import CategoryItem, SouqItem
from scrapy_redis.spiders import RedisSpider


log_indent = lambda t, s: t * 20 + s + t *20


class SellerSpider(RedisSpider):
    name = "sellers"

    """
    start_urls = [
        'https://uae.souq.com/ae-en/shop-all-categories/c'
    ]
    """

    def parse(self, response):
        self.logger.info(log_indent("=", "Finish Crawling the Index Page, Try to analyze detail page..."))
        main_block = response.xpath("//main[@class='main-section ']")[0]
        url_pool = []
        for block in main_block.xpath("div//div[@class='large-4 columns']"):
            shop_category = block.xpath("h3/text()").extract()
            group_category = block.xpath("div[@class='grouped-list']")
            self.logger.info("Total group numbers: {}".format(len(group_category)))
            for shop_title, group_block in zip(shop_category, group_category):
                self.logger.info("Extracting {} category...".format(shop_title))
                for group_a in group_block.xpath("ul//li[not(@class)]/a"):
                    group_link = group_a.xpath("@href").extract_first()
                    group_name = group_a.xpath("text()").extract_first()
                    # self.logger.info("Get link: {} for {}".format(group_link, group_name))
                    yield CategoryItem(parent=shop_title, name=group_name, link=group_link)
                    url_pool.append(group_link)

        self.logger.info(log_indent("=", "Start Analyzing the item pages..."))
        for link in url_pool:
            start_page = "{}?ref=nav&section=2&page=1".format(link)
            request = scrapy.Request(url=start_page, callback=self.parse_item_page)
            request.meta['ini_url'] = start_page
            yield request

    def parse_item_page(self, response):
        self.logger.info(log_indent("-", "Handling item page of {}".format(response.meta['ini_url'])))
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
            request_list.append(scrapy.Request(url=item_link, callback=self.parse_detail))

        # enqueue requests
        for request in request_list:
            yield request

        next_page = response.xpath("//li[@class='pagination-next goToPage']/a/@href").extract_first()
        
        if next_page is None:
            return

        request = scrapy.Request(url=next_page + "&section=2", callback=self.parse_item_page)
        request.meta['ini_url'] = next_page + "&section=2"
        yield request

    def parse_detail(self, response):
        try:
            product_title_block = response.xpath("//div[@class='small-12 columns product-title']")

            name = product_title_block.xpath("h1/text()").extract_first()
            category = product_title_block.xpath("span/a[2]/text()").extract_first()
            self.logger.info(log_indent(".", "Handle {}".format(name)))     
            link = response.url
    
            price_block = response.xpath("//section[@class='price-messaging']/div//h3[@class='price is sk-clr1']")
            raw_price = price_block.xpath("text()[2]").extract_first()
            if raw_price is None:
                # sold out
                return 
            price = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", raw_price)[0]
    
            description = "\n".join(response.xpath("//div[@class='item-details-mini clearfix']/ul/li/text()").extract())
    
            seller_block = response.xpath("//span[@class='unit-seller-link']/a")
    
            # check is amazon global
            if not seller_block:
                seller = "Amazon Global"
                seller_link = ""
            else:
                seller = seller_block.xpath("b/text()").extract_first()
                seller_link = response.xpath("@href").extract_first()
    
            update_at = datetime.datetime.now()
    
            # self.logger.info("::::Fetchr item {} - {} AED::::".format(name[10:], price))
            yield SouqItem(name=name, category=category, link=link, price=price, seller=seller, seller_link=seller_link,
                           description=description, update_at=update_at)
        except Exception as e:
            self.logger.error("Exception {}, try {} manually".format(e, link))
