# -*- coding:utf-8 -*-
# author: kusen
# email: 1194542196@qq.com
# date: 2023/5/23

import datetime

import gggdtparser

from gggne import utils
from gggne.configs import publish_time as publish_time_configs


class PublishTimeExtractor:
    @classmethod
    def extract(cls, text=None, element=None,
                element_text=None, url=None, **kwargs):
        return cls.extract_by_text(text, **kwargs) or cls.extract_by_element(
            element, **kwargs) or cls.extract_by_element_text(
            element_text, element, **kwargs) or cls.extract_by_url(
            url, **kwargs)

    @classmethod
    def extract_by_element_text(cls, element_text, element, **kwargs):
        if element_text:
            return cls.parse(element_text, **kwargs)
        if element is not None:
            return cls.parse(utils.element2string(element), **kwargs)

    @classmethod
    def extract_by_element(cls, element, **kwargs):
        if element is None:
            return
        head = element.find('head')
        if head is None:
            head = element
        text = utils.extract_from_html_meta_list(
            head, publish_time_configs.HTML_META_XPATH_LIST)
        return cls.parse(text, **kwargs)

    @classmethod
    def extract_by_url(cls, url, **kwargs):
        return cls.parse(url, **kwargs)

    @classmethod
    def extract_by_text(cls, text, **kwargs):
        return cls.parse(text, **kwargs)

    @classmethod
    def parse(cls, datetime_string, **kwargs):
        if not datetime_string:
            return
        return gggdtparser.parse(
            datetime_string,
            max_datetime=datetime.datetime.now(),
            **kwargs)
