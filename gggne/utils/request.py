# -*- coding:utf-8 -*-
# author: kusen
# email: 1194542196@qq.com
# date: 2023/6/6


import requests


def download(url, **kwargs):
    encoding = kwargs.pop('encoding', 'auto')
    for _ in range(3):
        try:
            response = requests.get(
                url, timeout=kwargs.pop('timeout', 30), **kwargs)
            if encoding == 'auto':
                response.encoding = response.apparent_encoding
            elif encoding:
                response.encoding = encoding
            return response.text
        except Exception as e:
            error = e
            continue
