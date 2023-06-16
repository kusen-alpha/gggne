# -*- coding:utf-8 -*-
# author: kusen
# email: 1194542196@qq.com
# date: 2023-05-28


from gggne import utils

HTML_META_XPATH_LIST = [
    r'//meta[contains(@name, "keywords")]/@content',
    r'//meta[contains(@property, "keywords")]/@content',
]


class KeyWordsExtractor:
    @classmethod
    def extract(cls, element):
        return utils.extract_from_html_meta_list(element, HTML_META_XPATH_LIST)
