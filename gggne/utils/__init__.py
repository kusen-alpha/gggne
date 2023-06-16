# -*- coding:utf-8 -*-
# author: kusen
# email: 1194542196@qq.com
# date: 2023/5/23
import hashlib
import re
import difflib
from lxml import etree
from lxml.etree import tostring


def extract_from_html_meta_list(element, meta_xpath_list):
    """

    :param element: html或head标签
    :param meta_xpath_list:
    :return:
    """
    for xpath in meta_xpath_list:
        result = ''.join(element.xpath(xpath)).strip()
        if not result:
            continue
        return result
    return ''


def extract_by_regex(text, regex_list):
    """
    抽取
    :param text:
    :param regex_list: 正则表达式格式有：()取其抽取内容，()()()取第2个抽取内容，
    其他取第一个抽取内容，没抽取到返回None
    :return:
    """
    for regex in regex_list:
        result_list = re.findall(regex, text)
        if not result_list:
            continue
        result = result_list[0]
        if isinstance(result, str):
            return result
        return result[1] if len(result) == 3 else result[0]


def element2string(element):
    return tostring(element, encoding='utf8').decode('utf8')


def string2element(s, base_url=None):
    return etree.HTML(s, base_url=base_url)


def lcs(str1, str2):
    matcher = difflib.SequenceMatcher(None, str1, str2)
    match = matcher.find_longest_match(0, len(str1), 0, len(str2))
    return str1[match.a:match.a + match.size]


def typecasting(value, value_type):
    if isinstance(value, list) and value_type == 'str':
        return ''.join(value).strip()
    return value


def extract_by_xpath_list(element, xpath_list, value_type=None):
    result = None
    for xpath in xpath_list:
        result = element.xpath(get_text_xpath(xpath))
        if result:
            break
    return typecasting(result, value_type)


def extract_by_regex_list(element_text, regex_list, value_type=None):
    result = None
    for regex in regex_list:
        result = re.findall(regex, element_text)
        if result:
            break
    return typecasting(result, value_type)


def get_text_xpath(xpath):
    xpath_list = xpath.split('|')
    new_xpath_list = []
    for _xpath in xpath_list:
        if not _xpath.endswith('//text()') and not _xpath.endswith(
                '/text()') and not re.findall(r'/@\w+$', xpath):
            _xpath = _xpath + '//text()'
        new_xpath_list.append(_xpath)
    xpath = '|'.join(new_xpath_list)
    return xpath


def extract(
        element_text, element,
        value_type=None, xpath_list=None,
        css_list=None, regex_list=None):
    if value_type is None:
        value_type = 'str'
    if xpath_list:
        result = extract_by_xpath_list(element, xpath_list, value_type)
        if result:
            return result
    if css_list:
        pass
    if regex_list:
        result = extract_by_regex_list(element_text, regex_list, value_type)
        if result:
            return result


def md5(s):
    _md5 = hashlib.md5()
    _md5.update(s.encode('utf8'))
    return _md5.hexdigest()