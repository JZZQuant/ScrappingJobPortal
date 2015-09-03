from scrapy import Request, Spider
from scrapy.exceptions import CloseSpider
from scrapy.selector import Selector
import scrapy
import settings

URL = 'http://www.hoovers.com/company-information/company-search.html?term=*&nvsls=[10;50L&nvind=1901&maxitems=100&page={page}'

class HooverItem(scrapy.Item):
    company = scrapy.Field()
    address = scrapy.Field()
    url = scrapy.Field()
    revenue = scrapy.Field()
    #telephone = scrapy.Field()
    #locality = scrapy.Field()
    #region = scrapy.Field()
    #country = scrapy.Field()
    site = scrapy.Field()
    FullAddress = scrapy.Field()

class Spider(Spider):
    handle_httpstatus_list = [404]
    name = "find"

    def start_requests(self):
        index = 1
        while index < 7 :           
            yield Request(URL.format(page=index))
            index +=1

    def parse(self, response):
        if response.status == 404:
            raise CloseSpider("Met the page which doesn't exist")

        sel = Selector(response)
        rows = sel.xpath('//tbody/tr')
        for row in rows:
            item = HooverItem()
            try:    
                url = str('http://www.hoovers.com' + row.xpath('td[1]/a/@href').extract()[0].strip())
                item['url']= url,
                try:
                    item['company'] = str(row.xpath('td[1]/a/text()').extract()[0].strip()),                
                except  :
                    pass
                try:
                    item['address']=str(row.xpath('td[2]/text()').extract()[0].strip()),
                except  :
                    pass
                try:
                    item['revenue']=str(row.xpath('td[3]/text()').extract()[0].strip()),
                except  :
                    pass
                item = Request(url=url,meta={'item': item},  callback=self.parse_item_page)
            except  :
                pass
            yield item               

    def parse_item_page(self, response):
        hxs = Selector(response)
        item = response.meta['item']
        try:
            item['FullAddress'] = str("  ,".join(hxs.xpath('.//p[@itemprop="address"]//span//text()').extract())).strip()
        except:
            pass
        #try:
        #    item['locality'] = str(hxs.xpath('.//p[@itemprop="address"]//span[2]//text()').extract()[0].strip())
        #except  :
        #    pass
        #try:
        #    item['region'] = str(hxs.xpath('.//p[@itemprop="address"]//span[3]//text()').extract()[0].strip())
        #except  :
        #    pass
        #try:
        #    item['country'] = str(hxs.xpath('.//p[@itemprop="address"]//span[4]//text()').extract()[0].strip())
        #except  :
        #    pass
        #try:
        #    item['telephone'] = str(hxs.xpath('.//p[@itemprop="address"]//span[5]//text()').extract())
        #except  :
        #    pass
        try:
            item['site'] = str(hxs.xpath('.//p[@itemprop="address"]//a//@href').extract()[0]).strip()
        except  :
            pass
        return item

        
