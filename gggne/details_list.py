# -*- coding:utf-8 -*-
# author: kusen
# email: 1194542196@qq.com
# date: 2023/6/5


import json
import re
import sys
import urllib
from collections import Counter

from lxml import etree
import pandas as pd

from gggne import utils
from gggne.utils.request import download

REGEX_MAP = {
    '/d': (re.compile(r'/\d{2,}'), r'/\\d+'),
    'd_': (re.compile(r'\d{2,}_'), r'\\d+_'),
    '-d': (re.compile(r'-\d{2,}'), r'-\\d+'),
    '_d': (re.compile(r'_\d{2,}'), r'_\\d+'),
    'd-': (re.compile(r'\d{2,}-'), r'\\d+-'),
    '=d': (re.compile(r'=\d+'), r'=\\d+'),
    '/w': (re.compile(r'/\w{2,}'), r'/\\w+'),
    '/w_': (re.compile(r'/\w+_'), r'/\\w+_'),
    'w_': (re.compile(r'\w+_'), r'\\w+_'),
    '_w': (re.compile(r'_\w+'), r'_\\w+'),
    'w+': (re.compile(r'\w{2,}'), r'\\w+'),
    '/dw': (re.compile(r'/(?=\w*\d)(?=\w*[a-zA-Z])\w+'), r'/\\w+'),
    'dw': (re.compile(r'(?=\w*\d)(?=\w*[a-zA-Z])\w+'), r'\\w+'),
    'w': (re.compile(r'^\w+$'), r'\\w+'),
    'd': (re.compile(r'^[0-9]+$'), r'\\d+'),
}

REDUCE_REGEX_LIST = [
    (re.compile(r'(/\\w\+){2,}'), r'(/\\w+)+'),
    (re.compile(r'(/\.\*)+'), '.*'),
]

PATH_SPLIT = '/'
PATH_ELEMENT_SPLIT_LIST = ['.', '-', '_']


class DetailListExtractor:
    @classmethod
    def extract(cls, element, domain_strictly=True):
        info, domain = cls.extract_urls(element, domain_strictly=domain_strictly)
        if not info:
            return {}
        # print(json.dumps(info))
        urls, paths = [], []
        for url, _info in info.items():
            urls.append(url)
            paths.append(_info['path'])
        urls, path_regex = cls.calculate_path(urls, paths)
        queries = [_info['query'] for url, _info in info.items() if url in urls]
        query_regex = '.*'
        if queries:
            urls, query_regex = cls.calculate_query(urls, queries)
        cls.calculate_query(urls, queries)
        result_regex = 'https?://' + domain + cls.reduce_regex(
            path_regex) + query_regex
        result = {'regex': result_regex, 'details': [], }
        for key, _info in info.items():
            if re.search(result_regex, key):
                r = {'url': key, 'title': _info['text']}
                result['details'].append(r)
                # print(key, _info['text'])
        # print(result_regex)
        # print(urls)
        return result

    @classmethod
    def can_split(cls, _list, sep_list):
        all_string = ''.join(_list)
        for sep in sep_list:
            if sep in all_string:
                return True, sep
        return False, None

    @classmethod
    def gen_regex(cls, s, name):
        regex_tuple = REGEX_MAP[name]
        return regex_tuple[0].sub(regex_tuple[1], s)

    @classmethod
    def gen_many_regex(cls, s, names):
        for name in names:
            s = cls.gen_regex(s, name)
        return s

    @classmethod
    def extract_urls(cls, element, domain_strictly=True):
        info = {}
        base_domain = urllib.parse.urlparse(element.base).netloc
        best_domain = None
        urls_dup = set()
        text_count = 0
        for ele in element.xpath('//a'):
            url = ele.get('href') or ele.get('HREF') or ''
            url = url.strip()
            if not url:
                continue
            if url in urls_dup:
                continue
            text = (''.join(ele.xpath('.//text()')) or ele.get(
                'title') or ele.get(
                'TITLE') or '').strip()
            text = text.replace(' ', '')
            if not text or len(text) <= 4:
                continue
            text_count += len(text)
            url = urllib.parse.urljoin(ele.base, url)
            url_parse = urllib.parse.urlparse(url)
            domain = url_parse.netloc
            if domain_strictly and base_domain != domain:
                continue
            urls_dup.add(url)
            _path = cls.gen_many_regex(
                url_parse.path, names=['/d', 'd_', '_d', '-d', 'd_', '/dw', 'dw'])
            _query = cls.gen_many_regex(url_parse.query, names=['=d'])
            _info = {
                'scheme': url_parse.scheme,
                'netloc': url_parse.netloc,
                'path': _path,
                'query': _query,
                'fragment': url_parse.fragment,
                'params': url_parse.params,
                'text': text,
                'text_count': len(text),
                'domain': domain
            }
            info[url] = _info
        if not urls_dup:
            return info, best_domain
        text_avg_half = text_count / len(urls_dup) / 2
        for key, _info in list(info.items()):
            if _info['text_count'] < text_avg_half:
                del info[key]
        if not domain_strictly:
            all_domains = [_info['domain'] for key, _info in info.items()]
            best_domain = Counter(all_domains).most_common()[0][0]
            for key, _info in list(info.items()):
                if _info['domain'] != best_domain:
                    del info[key]
        return info, best_domain or base_domain

    @classmethod
    def count_regex(cls, _list):
        counter = {
            r'\d+': 0,
            r'\w+': 0,
            r'.*': 0
        }
        for s in _list:
            if s == '*':
                counter[r'.*'] += 1
            if REGEX_MAP['d'][0].search(s) or s == '*' or s == '\\d+':
                counter[r'\d+'] += 1
            if REGEX_MAP['w'][0].search(s) or s == '*':
                counter[r'\w+'] += 1
        c = Counter(counter)
        if c[r'.*'] > len(_list) * 0.8:
            return r'.*'
        return c.most_common()[0][0]

    @classmethod
    def reduce_regex(cls, _regex):
        for rd in REDUCE_REGEX_LIST:
            _regex = rd[0].sub(rd[1], _regex)
        return _regex

    @classmethod
    def clear_df(cls, cdf, col_num=1):
        max_key = None
        for col, values in cdf.items():
            if col < col_num:
                continue
            elif col > col_num:
                return cdf, max_key
            c = Counter(values.tolist())
            count = sum(c.values())
            max_key, max_count = c.most_common()[0]
            if (
                    max_key == 'None' or max_key == ' ') and max_count >= count * 0.5:
                cdf = cdf[cdf[col].str.contains(re.escape(max_key))]
            elif max_key != '*' and max_count >= count * 0.8:
                cdf = cdf[cdf[col].str.contains(re.escape(max_key))]
            else:
                cdf = cdf[~cdf[col].str.contains('None')]
                cdf = cdf[~cdf[col].str.contains(' ', )]
                nl = cdf[col].values.tolist()
                can, sep = cls.can_split(nl, PATH_ELEMENT_SPLIT_LIST)
                if can:
                    ndf = cls.generate_df(cdf[0].values.tolist(), nl, sep)
                    ndf, max_key = cls.calculate_result(ndf, sep=sep)
                    cdf = cdf[cdf[0].isin(list(ndf[0].values))]
                else:
                    max_key = cls.count_regex(nl)  # 计算有*的
        return cdf, max_key

    @classmethod
    def generate_df(cls, keys, items, sep='/', regex_names=None):
        if not regex_names:
            regex_names = []
        items = [cls.gen_many_regex(item, regex_names) for item in items]
        lts = list(zip(keys, items))
        lts = [[t[0]] + t[1].split(sep) for t in lts]
        lts.sort(key=lambda x: len(x), reverse=True)
        # lts = lts[:10] + lts[-10:]
        ndf = pd.DataFrame(lts)  # new DataFrame
        ndf.replace('', ' ', inplace=True)
        ndf = ndf.fillna(value='None')
        # 对齐
        for index, row in ndf.iloc[1:].iterrows():
            prev_dst_col = sys.maxsize
            prev_src_col = None
            for column, value in row.iloc[:0:-1].items():
                if value in ['None', ' ', '*']:
                    continue
                else:
                    if not prev_src_col:
                        prev_src_col = column
                if value in set(ndf.iloc[:index, column]):
                    continue
                for col, v in ndf.iloc[:index,
                              prev_dst_col - 1:column:-1].items():
                    if value in set(v) and (
                            (prev_dst_col - col) >= (prev_src_col - column)):
                        offset = col - column
                        if column == prev_src_col:
                            prev_src_col += 1
                        for i in range(column, prev_src_col):
                            ndf.iat[index, i + offset] = ndf.iat[index, i]
                            ndf.iat[index, i] = '*'
                        prev_dst_col = col
                        prev_src_col = column
                        break
        return ndf

    @classmethod
    def calculate_result(cls, df, sep='/'):
        keys = []
        for col in range(1, len(df.columns) + 1):
            df, max_key = cls.clear_df(df, col)
            if max_key is not None and max_key not in ['None']:
                keys.append(max_key)
        return df, sep.join(keys).strip()

    @classmethod
    def calculate_query(cls, urls, queries):
        gdf = cls.generate_df(urls, queries, sep='&')
        for column, value in gdf.iloc[:, 1:].items():
            if 'None' in value.tolist():
                gdf[column] = 'None'
        # print(gdf)
        rdf, regex = cls.calculate_result(gdf)
        urls = list(rdf[0].values)
        regex = '\?.*?' + regex + '.*' if regex else '.*'
        return urls, regex

    @classmethod
    def calculate_path(cls, urls, paths):
        gdf = cls.generate_df(urls, paths)
        # print(gdf)
        rdf, regex = cls.calculate_result(gdf)
        urls = list(rdf[0].values)
        # print(result_urls)
        # print(len(result_urls))
        return urls, regex


def download_and_extract(url, domain_strictly=True, **kwargs):
    text = download(url, **kwargs)
    if not text:
        return {}
    html = utils.string2element(text, base_url=url)
    return extract(html, domain_strictly=domain_strictly)


def extract(html, domain_strictly=True):
    return DetailListExtractor.extract(html, domain_strictly=domain_strictly)
