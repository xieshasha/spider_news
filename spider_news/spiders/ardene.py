# -*- coding: utf-8 -*-
import scrapy
import sys
if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')
import urllib
class XpathRule(object):
    classify = "//a[@class='has-sub-menu top-level-tag']"
    lis = "//div[@class='pagination']/ul/li/a"
    dress = "//li[@class='grid-tile']//div[@class='product-tile__content-sync']"
    detailPic = "//li[contains(@class,'thumb')]"
    selectable = "//ul[@class='main-size-container']/li[@class='selectable']/a[@class='swatchanchor']"
    colors = "//a[@class='swatchanchor']/@colordisplayvalue"
    description = "//div[@class='tab-content']//text()|//div[@class='tab-content']/text()"



class ArdeneSpider(scrapy.Spider):
    name = "ardene"
    custom_settings = {
        'CONCURRENT_REQUESTS': 16,
        # 'DUPEFILTER_CLASS': "toutiao_video.dupefilters.toutiao_dupefilter.ToutiaoDupeFilter",
        'ITEM_PIPELINES': {
            "spider_news.pipelines.SpiderPipeline": 200,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'spider_news.middlewares.RandomUserAgent.RandomUserAgent': 300,
        }
    }
    start_urls = ['https://www.ardene.com/ca/en/homepage/']

    def parse(self, response):  # 翻页
        classify = response.xpath(XpathRule.classify)
        for case in classify[:-2]:
            url = case.xpath("@href").extract()[0]
            name = case.xpath("text()").extract()[0].strip()  #商品分类

            yield scrapy.Request(url, callback=self.get_classify_page, meta={"name": name})

    def get_classify_page(self, response):
        lis = response.xpath(XpathRule.lis)
        if len(lis)>=2:
            totalpage = lis[-2].xpath("text()").extract()[0]
            for page in range(int(totalpage)):
                pageNum = page * 50
                pageUrl = response.url + "?sz=50&start={}".format(pageNum)
                yield scrapy.Request(pageUrl, callback=self.get_classify_info, meta={"name": response.meta['name']})
        else:
            print "该类别无商品："+response.meta["name"]

    def get_classify_info(self, response):
        '''
        brand-品牌     ardene
        name-商品名字
        priceA-折扣之前
        price-N 折扣之后
        priceK-单位
        detailL-详情链接
        retailer-域名
        sizes-还剩下什么号码
        pic1-详情页的所有图片 以；分割  colors-颜色  level1-商品属于的分类
        '''
        dresses = response.xpath(XpathRule.dress)
        for dress in dresses:
            dressName = dress.xpath("./div[@class='product-name']/a/text()").extract()[0].strip()  #商品名字
            dressUrl = dress.xpath("./div[@class='product-name']/a/@href").extract()[0]   #详情链接
            product_standard_price = dress.xpath("./div[@class='product-pricing']/span[@class='product-standard-price ']/text()").extract()
            product_sales_price = dress.xpath("./div[@class='product-pricing']/span[@class='product-sales-price ']/text()").extract()
            proto, rest = urllib.splittype(dressUrl)
            retailer, rest = urllib.splithost(rest)
            if product_standard_price and product_sales_price:
                priceStart = product_standard_price[0] #折扣之前
                priceEnd = product_sales_price[0]  #折扣之后
                yield scrapy.Request(dressUrl, callback=self.get_detail_info,
                                     meta={"name": response.meta['name'],"dressName":dressName,
                                           "retailer":retailer.split(".")[1].upper(),"priceStart":priceStart,
                                           "priceEnd":priceEnd})

    def get_detail_info(self,response):

        detailPic = response.xpath(XpathRule.detailPic)
        pics=[]
        for pic in detailPic:
            img = pic.xpath(".//img[@class='productthumbnail']/@src").extract()[0].strip()
            pics.append(img)
        pic1=';'.join([item for item in pics])
        selectables = response.xpath(XpathRule.selectable)
        sz = []
        for size in selectables:
            sz.append(size.xpath("text()").extract()[0].strip())
        sizes = ",".join([item for item in sz])
        if not sizes:
            sizes="onesizes"
        colors = response.xpath(XpathRule.colors)
        cs = []
        for color in colors:
            cs.append(color.extract())
        clrs = ",".join([item for item in cs])
        level = response.meta["name"]
        descriptions = response.xpath(XpathRule.description).extract()
        if descriptions:
            description = "".join([item for item in descriptions])

        item = {}
        item['brand']=u"ardene"
        item['name'] = response.meta['dressName']
        item['priceAfter'] = response.meta['priceStart'].replace("$","")
        item['priceNow'] = response.meta['priceEnd'].replace("$","")
        item['priceKind'] = '$'
        item['detailLink'] = response.url
        item['description'] = description
        item['retailer'] = response.meta['retailer']
        item['sizes']=sizes
        item['pic1']=pic1
        item['colors']=clrs
        item['level1']="women"+";"+level
        item['tableName']="Search_test"
        yield item


