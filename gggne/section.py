# -*- coding:utf-8 -*-
# author: kusen
# email: 1194542196@qq.com
# date: 2023/6/5
import copy
import math
from urllib.parse import urljoin
from urllib.parse import urlparse

from gggne import utils
from gggne.utils.request import download


class SectionExtractor:
    @classmethod
    def extract(cls, element, domain_strictly=False):
        """

        :param element: etree._Element对象或子类对象
        :param domain_strictly: 是否进行域名过滤，True时必须element设置base_url
        :return:
        """
        element = copy.deepcopy(element)
        body = element.find('body')
        if body is None:
            body = element
        root_tree = body.getroottree()
        cls.clear_body(body, root_tree, domain_strictly)
        info = cls.calculate_score(body, root_tree)
        sort_result = sorted(
            info.items(), key=lambda x: x[1]['score'], reverse=True)
        best_element = sort_result[0][1]['element']
        result = []
        for a in best_element.xpath('.//a'):
            item = {'url': a.get('href') or a.get('HREF'),
                    'title': ''.join(a.xpath('.//text()')).strip()}
            result.append(item)
        result.sort(key=lambda x: len(x['url'].split('/')))
        last_result = {}
        for item in result:
            for _url, _title in list(last_result.items()):
                if _url in item['url']:
                    last_result[item['url']] = _title + '-' + item['title']
            else:
                last_result[item['url']] = item['title']
        for _id, _info in list(info.items()):
            del _info['element']
        # print(json.dumps(sort_result, ensure_ascii=False))
        # print(etree.tostring(body, encoding='utf8').decode('utf8'))
        return [{'url': url, 'title': title} for url, title in
                last_result.items()]

    @classmethod
    def increase_parent_score(cls, info, parent_id, times):
        if not parent_id:
            return
        _info = info.get(parent_id)
        if not _info:
            return
        tag = _info['tag']
        element = _info['element']
        attr_str = ''.join([element.get('id') or '',
                            element.get('class') or '']).strip().lower()
        for s in ['nav', 'menu']:
            if s in attr_str:
                _info['score'] *= times
        if tag in ['li', 'ul', 'ol', 'nav']:
            _info['score'] *= times
            cls.increase_parent_score(info, _info['parent_id'], times)
        else:
            _info['score'] *= math.sqrt(times)
            cls.increase_parent_score(info, _info['parent_id'],
                                      math.sqrt(times))

    @classmethod
    def clear_body(cls, body, root_tree, domain_strictly):
        base_url = body.base
        base_domain = urlparse(base_url).netloc
        if not base_domain:
            domain_strictly = False
        urls_dup = set()
        info = {}
        index = 0
        a_text_count = 0
        a_count = 0
        for element in cls.element_iter(body):
            _info = {}
            _id = root_tree.getpath(element)
            parent = element.getparent()
            parent_id = None
            if parent is not None:
                parent_id = root_tree.getpath(parent)
            _info['parent_id'] = parent_id
            _info['tag'] = str(element.tag)
            _info['text'] = ''
            _info['text_count'] = 0
            domain = ''
            href = ''
            if _info['tag'] == 'a':
                _info['text'] = (element.text or
                                 element.tail or '').strip() or ''.join(
                    element.xpath('.//text()')).strip()
                _info['text_count'] = len(_info['text'])
                href = (element.get('href') or element.get(
                    'HREF') or '').strip()
                href = urljoin(base_url, href)
                element.set('href', href)
                href_parse = urlparse(href)
                _path = href_parse.path
                if _path in urls_dup:
                    href = ''
                else:
                    urls_dup.add(_path)
                domain = href_parse.netloc
                a_text_count += _info['text_count']
                a_count += 1
            _info['index'] = index
            _info['element'] = element
            _info['href'] = href
            _info['domain'] = domain
            _info['has_a'] = bool(element.xpath(
                './/a')) or cls.parents_has_element(element, ['a'])
            info[_id] = _info
            index += 1
        a_text_avg_count = a_text_count / a_count
        half_index = index * 0.5
        for _id, _info in info.items():
            element = _info['element']
            if _info['tag'] == 'a':
                if (_info['text_count'] >= a_text_avg_count or
                        _info['text_count'] < 2):
                    element.getparent().remove(element)
                    continue
                if base_domain and not _info['href'].startswith('http'):
                    element.getparent().remove(element)
                    continue
                if domain_strictly and _info['domain'] != base_domain:
                    element.getparent().remove(element)
                    continue
            if _info['index'] >= half_index:
                element.getparent().remove(element)
        for ele in cls.element_iter(body):
            if ele.tag == 'a':
                continue
            if ele.xpath('.//a') or cls.parents_has_element(ele, ['a']):
                continue
            ele.getparent().remove(ele)

    @classmethod
    def calculate_score(cls, body, root_tree):
        info = {}
        for element in cls.element_iter(body):
            a_count = len(element.xpath('.//a'))
            all_count = len(element.xpath('.//*')) or 1
            score = a_count / all_count
            parent = element.getparent()
            parent_id = None
            if parent is not None:
                parent_id = root_tree.getpath(parent)
            _info = {'score': score, 'element': element,
                     'parent_id': parent_id, 'tag': str(element.tag),
                     'text': ''.join(element.xpath('./text()')).strip(),
                     'attrib': dict(element.attrib)
                     }
            info[root_tree.getpath(element)] = _info
        for _id, _info in info.items():
            if _info['tag'] in ['a', ]:
                cls.increase_parent_score(info, _info['parent_id'], 2)
            elif _info['tag'] in ['li', 'ul', 'nav']:
                _info['score'] *= 2
        return info

    @classmethod
    def parents_has_element(cls, element, tags=None):
        if not tags:
            tags = []
        parent = element.getparent()
        while parent is not None:
            if parent.tag in tags:
                return True
            parent = parent.getparent()
        return False

    @classmethod
    def element_iter(cls, element):
        yield element
        for ele in element:
            yield from cls.element_iter(ele)


def download_and_extract(url, domain_strictly=True, **kwargs):
    """

    :param url:
    :param domain_strictly:
    :param kwargs: 请求相关参数
    :return:
    """
    text = download(url, **kwargs)
    if not text:
        return []
    html = utils.string2element(text, base_url=url)
    return extract(html, domain_strictly)


def extract(html, domain_strictly=True):
    return SectionExtractor.extract(html, domain_strictly)
