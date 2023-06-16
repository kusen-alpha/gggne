# -*- coding:utf-8 -*-
# source: kusen
# email: 1194542196@qq.com
# date: 2023/5/23


from gggne import utils
from gggne.configs import source as source_configs


class SourceExtractor:

    @classmethod
    def extract(cls, text=None, element=None, element_text=None, default=None):
        """

        :param element: 一般为html或head标签
        :param element_text: 一般为html或head标签
        :param text: 经过模糊抽取后的内容，需要进一步抽取
        :param default: 默认值
        :return:
        """
        return cls.extract_by_text(text) or cls.extract_by_element(
            element) or cls.extract_by_element_text(
            element_text, element) or default

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
            text, source_configs.EXTRACT_REGEX_LIST)

    @classmethod
    def extract_by_element(cls, element):
        if element is None:
            return
        text = utils.extract_from_html_meta_list(
            element, source_configs.HTML_META_XPATH_LIST)
        source = cls._extract_by_text(text)
        if source:
            return source
        return text

    """
    class=artiSource
    """