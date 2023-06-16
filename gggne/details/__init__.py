# -*- coding:utf-8 -*-
# author: kusen
# email: 1194542196@qq.com
# date: 2023/6/5

import re

import requests

from gggne import utils
from gggne.details.author import AuthorExtractor
from gggne.details.title import TitleExtractor
from gggne.details.source import SourceExtractor
from gggne.details.publish_time import PublishTimeExtractor
from gggne.details.content import ContentExtractor
from gggne.details.description import DescriptionExtractor


def download_and_extract(
        url, title_config=None,
        content_config=None, publish_time_config=None,
        source_config=None, author_config=None, **kwargs):
    config_kwargs = {}
    for key in list(kwargs.keys()):
        if key.endswith('config'):
            config_kwargs[key] = kwargs.pop(key)
    encoding = kwargs.pop('encoding', None)
    error = None
    for _ in range(3):
        try:
            response = requests.get(
                url, timeout=kwargs.pop('timeout', 30), **kwargs)
            if encoding == 'auto':
                response.encoding = response.apparent_encoding
            elif encoding:
                response.encoding = encoding
            break
        except Exception as e:
            error = e
            continue
    else:
        return {}
    html = utils.string2element(response.text)
    return extract(
        response.text, html, url, title_config=title_config,
        content_config=content_config, publish_time_config=publish_time_config,
        source_config=source_config, author_config=author_config,
        **config_kwargs
    )


def extract(html_text, html=None, base_url=None, title_config=None,
            content_config=None, publish_time_config=None,
            source_config=None, author_config=None, **other_configs):
    """

    :param html_text:
    :param html:
    :param base_url:
    :param title_config: {'value_type': 'str', 'xpath_list': [],
        'css_list': [], 'regex_list': [], }
    :param content_config:
    :param publish_time_config:
    :param source_config:
    :param author_config:
    :param other_configs:
    :return:
    """
    if not content_config:
        content_config = {}
    result = {}
    if html is None:
        html_text = re.sub('</?br.*?>', '\n', html_text)
        html = utils.string2element(html_text)
    text = ' '.join(html.xpath('//text()')).strip()
    result['title'] = utils.extract(
        html_text, html, **(title_config or {})) or TitleExtractor.extract(html)
    _author = utils.extract(html_text, html, **(author_config or {}))
    result['author'] = AuthorExtractor.extract(
        text=(_author or text),
        element=html, element_text=html_text, default=_author)
    _source = utils.extract(html_text, html, **(source_config or {}))
    result['source'] = SourceExtractor.extract(
        text=(_source or text),
        element=html, element_text=html_text, default=_source)
    publish = PublishTimeExtractor.extract(
        text=utils.extract(html_text, html, **(publish_time_config or {})),
        element=html, element_text=html_text, url=base_url)
    publish_string = None
    if publish:
        publish_string = publish.strftime('%Y-%m-%d %H:%M:%S')
        publish = int(publish.timestamp())
    result['publish_time'] = publish
    result['string_publish_time'] = publish_string
    for key, value in other_configs.items():
        result[key.replace('_config', '')] = utils.extract(
            html_text, html, **(value or {}))
    result.update(ContentExtractor.extract(
        html, html_text, mark=content_config.get('mark') or True))
    return result
