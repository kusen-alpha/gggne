# -*- coding:utf-8 -*-
# author: kusen
# email: 1194542196@qq.com
# date: 2023/5/23

from gggne import utils
from gggne.configs import author as author_configs


# class="writer"
# class="user-name"
# <span class="bjh-p">记者 吴乐珺 李应齐</span><

class AuthorExtractor:
    @classmethod
    def extract(cls, text=None, element=None, element_text=None, default=None):
        """

        :param element: 一般为html或head标签
        :param element_text: 一般为html或head标签
        :param text: 经过模糊抽取后的内容，需要进一步抽取
        :param default: 默认值
        :return:
        """
        return cls.extract_by_text(text) or cls.extract_by_element_text(
            element_text, element) or cls.extract_by_element(
            element) or default

    @classmethod
    def extract_by_text(cls, text, ):
        return cls._extract_by_text(text)

    @classmethod
    def extract_by_element_text(cls, element_text, element):
        if element_text:
            return cls._extract_by_text(element_text)
        if element is not None:
            return cls._extract_by_text(utils.element2string(element))

    @classmethod
    def _extract_by_text(cls, text):
        if not text:
            return
        return utils.extract_by_regex(
            text, author_configs.EXTRACT_REGEX_LIST)

    @classmethod
    def extract_by_element(cls, element):
        if element is None:
            return
        text = utils.extract_from_html_meta_list(
            element,
            author_configs.HTML_META_XPATH_LIST) or cls.extract_by_element_attrib(
            element)
        author = cls._extract_by_text(text)
        if author:
            return author
        return text

    @classmethod
    def extract_by_element_attrib(cls, element):
        for attrib in author_configs.ELEMENT_ATTRIB_LIST:
            result = ''.join(element.xpath(
                './/*[@class="%s"]/text()' % attrib)).strip()
            if result:
                return result
        return ''
