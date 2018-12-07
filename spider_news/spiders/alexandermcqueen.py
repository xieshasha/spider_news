# -*- coding: utf-8 -*-
import scrapy
import sys
import re
import json
if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')
import urllib
class XpathRule(object):
    classify = "//ul[@class='level-3']//@href"
    names = "//ul[@class='level-3']//span[@class='text']/text()"
    Items = "//div[@class='products product-list']/article[@class=' item']/a/@href"
    details = "//div[@class='productInfoContainer']"
    images = "//div[@class='productImages']/ul[@class='alternativeImages']/li/img/@src"



class AlexandermcqueenSpider(scrapy.Spider):
    name = "AlexandermcqueenSpider"
    custom_settings = {
        'CONCURRENT_REQUESTS': 16,
        'ITEM_PIPELINES': {
            "spider_news.pipelines.SpiderPipeline": 200,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'spider_news.middlewares.RandomUserAgent.RandomUserAgent': 300,
        }
    }
    start_urls = ['https://www.alexandermcqueen.cn/cn']

    def parse(self, response):  # 翻页
        classify = response.xpath(XpathRule.classify)
        names = response.xpath(XpathRule.names).extract()
        flag=False
        for case in classify:
            url =case.extract().strip()
            name = names[classify.index(case)]  #level1
            if name=="当季新品上线":
                flag = True
            if not flag:
                name = "女士;"+name
            else:
                name="男士;"+name

            yield scrapy.Request(url, callback=self.get_classify_page, meta={"name": name})

    def get_classify_page(self, response):
        items = response.xpath(XpathRule.Items)
        for item in items:
            leve2Url = item.extract()
            yield scrapy.Request(leve2Url, callback=self.get_classify_info, meta={"name": response.meta['name']})


    def get_classify_info(self, response):
        details = response.xpath(XpathRule.details)
        images = response.xpath(XpathRule.images)
        proto, rest = urllib.splittype(response.url)
        retailer, rest = urllib.splithost(rest)
        for detail in details:
            name = detail.xpath(".//*[@class='modelName']/text()").extract()[0].strip()
            price = detail.xpath(".//span[@class='value']/text()").extract()[0].strip().replace(",","")
            descriptions=detail.xpath(".//div[@class='descriptionsContainer']//text()").extract()
            description = "".join([item.replace("\n","").strip() for item in descriptions])
        if "cod10" in response.url:
            code10=re.compile("cod10=(.*?)&").search(response.url).group(1)
        else:
            code10=re.compile("cod(.*?)\.html").search(response.url).group(1)
        detailApi = "https://www.alexandermcqueen.cn/yTos/api/Plugins/ItemPluginApi/GetCombinationsAsync/?siteCode=ALEXANDERMCQUEEN_CN&code10={}".format(code10)
        pics = []
        for image in images:
            pics.append(image.extract().strip())
        pic1 = ';'.join([item for item in pics])
        item = {}
        item['brand'] = u"alexandermcqueen"
        item['name'] = name
        item['priceAfter'] = price
        item['priceNow'] = price
        item['priceKind'] = '￥'
        item['detailLink'] = response.url
        item['description'] = description
        item['retailer'] = retailer.split(".")[1].upper()
        item['pic1'] = pic1
        # item['colors'] = colors
        item['level1'] = response.meta["name"]
        item['tableName'] = "Search_test"
        yield scrapy.Request(detailApi, callback=self.get_detail_info,meta={"item": item})


    def get_detail_info(self,response):
        jsonData = json.loads(response.body)
        colors = jsonData.get("Colors",[])
        items=response.meta["item"]
        clrs=[]
        for color in colors:
            clrs.append(color.get("Description",""))
        clr = ','.join([item for item in clrs])
        sizes=[]
        for sz in jsonData.get("Sizes",[]):
            Description1 = sz.get("Description","")
            if "Alternative" in sz.keys():
                if sz.get("Alternative",{}) is not None:
                    Description2 = sz.get("Alternative",{}).get("Description","")
                    sizes.append(str(Description2) + "-" + str(Description1))
            else:
                sizes.append(str(Description1))
        size = ','.join([item for item in sizes])
        if not size:
            size="onesizes"
        items['sizes'] = size
        items['colors'] = clr
        yield items







