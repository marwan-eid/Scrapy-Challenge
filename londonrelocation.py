import scrapy
from scrapy import Request
from scrapy.loader import ItemLoader
from scrapy.http import HtmlResponse
from property import Property
import re


class LondonrelocationSpider(scrapy.Spider):
    name = 'londonrelocation'
    allowed_domains = ['londonrelocation.com']
    start_urls = ['https://londonrelocation.com/properties-to-rent/']

    def parse(self, response):
        for start_url in self.start_urls:
            yield Request(url=start_url, callback=self.parse_area)

    def parse_area(self, response):
        area_urls = response.xpath(
            './/div[contains(@class,"area-box-pdh")]//h4/a/@href').extract()
        for area_url in area_urls:
            yield Request(url=area_url,
                          callback=self.parse_area_pages)

    def parse_area_pages(self, response):
        last_page_url = str(response.xpath(
            './/div[contains(@class,"pagination")]//ul/li/a/@href')[-1].extract())
        no_pages = int(last_page_url[last_page_url.find('&') + 9:])
        # The loop for travesing all pages would be as follows:
        # for page_no in range(1, no_pages):
        #     page_url = str(response) + "&pageset=" + str(page_no)
        #     #scraping from page_url (similar to the code below)
        # However, we traverse only 2 pages (if applicable) as a proof of concept
        no_pages_to_scrape = 2
        page_no = 0
        # no. of pages > 2 (i.e. more than 20 properties since each page has 10 propoerties)
        # I decided to check if the page number (pageset) is applicable using this approach (getting
        # the last page in pagination and retrieving this page's number) instead of checking if the
        # page is not None, because in this website, if you specified any large number in the pageset
        # field in the url, it would probably retrieve the last page in the specified keyword, which
        # means the condition would always be true since the page exists anyway whether the page number
        # is applicable or not.
        if (no_pages >= no_pages_to_scrape):
            while (page_no < no_pages_to_scrape):
                page_no += 1
                page_url = str(response) + "&pageset=" + str(page_no)
                response = HtmlResponse(url=page_url)
                titles = response.xpath(
                    '//div[contains(@class,"h4-space")]/h4/a/text()').extract()
                urls = response.xpath(
                    '//div[contains(@class,"h4-space")]/h4/a/@href').extract()
                prices = response.xpath(
                    '//div[contains(@class,"bottom-ic")]/h5/text()').extract()
                base_url = "https://londonrelocation.com"
                urls = [base_url + url for url in urls]
                for item_index in range(len(titles)):
                    property = ItemLoader(item=Property())
                    property.add_value('title', titles[item_index].strip())
                    if ("pw" in prices[item_index]):
                        property.add_value('price', str(
                            int(re.sub("[^0-9]", "", prices[item_index])) * 4))
                    else:
                        property.add_value('price', str(
                            int(re.sub("[^0-9]", "", prices[item_index]))))
                    property.add_value('url', urls[item_index])
                    yield property.load_item()
        elif (no_pages == 1):  # this location (i.e. keyword) has only 1 page of properties
            titles = response.xpath(
                '//div[contains(@class,"h4-space")]/h4/a/text()').extract()
            urls = response.xpath(
                '//div[contains(@class,"h4-space")]/h4/a/@href').extract()
            prices = response.xpath(
                '//div[contains(@class,"bottom-ic")]/h5/text()').extract()
            base_url = "https://londonrelocation.com"
            urls = [base_url + url for url in urls]
            for item_index in range(len(titles)):
                property = ItemLoader(item=Property())
                property.add_value('title', titles[item_index].strip())
                if ("pw" in prices[item_index]):
                    property.add_value('price', str(
                        int(re.sub("[^0-9]", "", prices[item_index])) * 4))
                else:
                    property.add_value('price', str(
                        int(re.sub("[^0-9]", "", prices[item_index]))))
                property.add_value('url', urls[item_index])
                yield property.load_item()
