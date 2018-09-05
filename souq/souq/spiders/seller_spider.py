import scrapy

from souq.items import CategoryItem


class SellerSpider(scrapy.Spider):
    name = "sellers"

    start_urls = [
        'https://uae.souq.com/ae-en/shop-all-categories/c'
    ]

    def parse(self, response):
        self.logger.info("Finish Crawling the Index Page, Try to analyze detail page...")
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

        for link in url_pool:
            yield scrapy.Request(url=link, callback=self.parse_detail)

    def parse_detail(self, response):
        pass
