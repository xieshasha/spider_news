# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import traceback
import MySQLdb


class SpiderPipeline(object):
    cc = '''INSERT IGNORE into Search_test(brand,name,priceAfter,priceNow,priceKind,detailLink,description,retailer,sizes,pic1,colors,level1,tableName)value(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
    conn = MySQLdb.connect(
        host='',
        port=3306,
        user='worker',
        passwd='worker',
        db='paper_recomder',
        charset="utf8"
    )
    cur = conn.cursor()

    def process_item(self, item, spider):
        try:
            insertdata = (
                item['brand'],
                item['name'],
                item['priceAfter'],
                item['priceNow'],
                item['priceKind'],
                item['detailLink'],
                item['description'],
                item['retailer'],
                item['sizes'],
                item['pic1'],
                item['colors'],
                item['level1'],
                item['tableName']
                )

            self.cur.execute(self.cc, insertdata)
            self.conn.commit()
        except Exception as errinfo:
            traceback.print_exc()
        return item

    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()