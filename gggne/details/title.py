# -*- coding:utf-8 -*-
# author: kusen
# email: 1194542196@qq.com
# date: 2023/5/23

from gggne import utils
from gggne.configs import title as title_configs


class TitleExtractor:

    @classmethod
    def extract(cls, element):
        """

        :param element: html或body标签
        :return:
        """
        head = element.find('head')
        if head is not None:
            head = element
        body = element.find('body')
        if body is not None:
            body = element
        title_tag_result = cls.get_by_title_tag(head)
        h_tag_result = cls.get_by_h_tag(body) or cls.get_by_other_tag(element)
        if not title_tag_result:
            if h_tag_result:
                return h_tag_result[0]
            return ''
        if not h_tag_result:
            return title_tag_result
        title = ''
        for _h_tag_result in h_tag_result:
            lcs_result = utils.lcs(title_tag_result, _h_tag_result)
            if len(lcs_result) > len(title) and len(lcs_result) >= 5:
                title = lcs_result
        return title

    @classmethod
    def get_by_h_tag(cls, element):
        result = []
        for xpath in title_configs.H_TAG_XPATH_LIST:
            content = ''.join(element.xpath(xpath)).strip()
            if content:
                result.append(content)
        return result

    @classmethod
    def get_by_title_tag(cls, element):
        title_elements = element.xpath('//title')
        if title_elements:
            return ''.join(title_elements[0].xpath('.//text()'))

    @classmethod
    def get_by_other_tag(cls, element):
        return element.xpath('//div[@class="title"]//text()')
