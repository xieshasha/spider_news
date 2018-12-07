# -*- coding: utf-8 -*-
import logging
import random
import requests
from scrapy.utils.response import response_status_message
from scrapy.downloadermiddlewares.retry import RetryMiddleware
logger = logging.getLogger(__name__)


class IpMiddleware(object):
    def __init__(self, settings):
        pass
        # 获取ip列表
        # self.get_ip_url = ""
        # self.proxy_ip = self.get_ip()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        request.meta['proxy'] = ""
        return None


    def process_response(self, request, response, spider):
        if response.status == 403:
            self.proxy_ip = self.get_ip()
            fail_res = request.copy()
            fail_res.dont_filter = True
            print fail_res.url
            return fail_res
        return response


