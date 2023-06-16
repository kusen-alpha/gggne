# -*- coding:utf-8 -*-
# author: kusen
# email: 1194542196@qq.com
# date: 2023/5/23


import re
import copy
import math


from lxml import etree

from gggne.configs import content as content_configs
from gggne.details.multi_media import MultiMediaExtract


class ContentExtractor:
    @classmethod
    def extract(cls, element, element_text='', mark=True):
        element = copy.deepcopy(element)  # 不影响原element结构
        body = element.find('body')
        if body is None:
            body = element
        cls.remove_useless_element(body, content_configs.REMOVE_UNLESS_TAGS)
        root_tree = body.getroottree()
        root_path = root_tree.getpath(body)
        info = {}
        index = 0
        for element in body.iter():
            parent = element.getparent()
            if cls.judge_not_element_and_remove(parent, element):
                continue
            if cls.judge_element_attrib_and_remove(
                    parent, element,
                    content_configs.REMOVE_ELEMENT_ATTRIB_VALUES):
                continue
            cls.remove_empty_element(
                parent, element, content_configs.EXCLUDE_EMPTY_ELEMENT_TAGS)
        for element in body.iter():
            parent = element.getparent()
            element_id = root_tree.getpath(element)
            if not element_id.startswith(root_path):
                continue
            _info = {'id': element_id}
            if parent is not None:
                parent_id = root_tree.getpath(parent)
                _info['parent_id'] = parent_id
            children = element.getchildren()
            _info['children_ids'] = []
            for child in children:
                _info['children_ids'].append(root_tree.getpath(child))
            siblings = list(etree.SiblingsIterator(element)) + list(
                etree.SiblingsIterator(element, preceding=True))
            _info['sibling_ids'] = []
            for sibling in siblings:
                _info['sibling_ids'].append(root_tree.getpath(sibling))
            _info['index'] = index
            attrib = dict(element.attrib)
            _info['attrib'] = attrib
            _info['import_attrib_value'] = ' '.join(
                [attrib.get('class', ''), attrib.get('id', '')]).strip()
            _info['element'] = element
            info.setdefault(element_id, {})
            info[element_id].update(_info)
            cls.calc_element_tdi(info, root_tree, element, element_id)
            cls.calc_element_sbdi(info, element_id)
            cls.calc_element_p_count(info, element, element_id)
            index += 1
        cls.calc_elements_score(info, index)
        cls.recalc_elements_score(info, index)
        sort_result = sorted(
            info.items(), key=lambda x: x[1]['score'], reverse=True)
        if not sort_result:
            return ''
        best = sort_result[0][1]
        content_element = best['element']
        cls.handle_content_element(content_element)
        content_raw = etree.tostring(
            content_element, encoding='utf8').decode('utf8')

        result = MultiMediaExtract.extract(
            content_element, element_text, mark=mark)
        result['content_raw'] = content_raw
        for key in info:
            info[key]['element'] = None
        # print(json.dumps(sort_result, ensure_ascii=False))
        return result

    @classmethod
    def judge_not_element_and_remove(cls, parent, element):
        if isinstance(element, etree._Comment):
            parent.remove(element)
            return True
        if not isinstance(element, etree._Element):
            parent.remove(element)
            return True

    @classmethod
    def judge_empty_element(cls, element):
        if element.getchildren():
            return False
        if element.text and element.text.strip():
            return False
        if element.tail and element.tail.strip():
            return False
        return True

    @classmethod
    def remove_empty_element(cls, parent, element, exclude_tags):
        _parent = element.getparent()
        if element.tag not in exclude_tags and cls.judge_empty_element(element):
            parent.remove(element)
        else:
            return
        cls.remove_empty_element(_parent.getparent(), _parent, exclude_tags)

    @classmethod
    def remove_useless_element(cls, element, useless_tags):
        etree.strip_elements(element, *useless_tags)

    @classmethod
    def judge_element_attrib_and_remove(cls, parent, element, attrib):
        class_attrs = element.get('class') or element.get('id') or ''
        for attr in attrib:
            if attr == class_attrs:
                if element in parent:
                    parent.remove(element)
                    return True

    @classmethod
    def get_element_text(cls, info, root_tree, element, element_id=None):
        if not element_id:
            element_id = root_tree.getpath(element)
            info.setdefault(element_id, {})
        text = info[element_id].get('text')
        if text is not None:
            return text
        text_list = []
        for _text in element.xpath('.//text()'):
            _text = _text.strip()
            if _text:
                _text = re.sub(r'[ \n\t\r\s]', '', _text)
                text_list.append(_text)
        if element.tag != 'a':
            for _ in element.xpath('.//img|.//video|.//audio|.//file'):
                text_list.append('多媒体占位符')
        text = ''.join(text_list)
        info[element_id]['text'] = text
        return text

    @classmethod
    def calc_element_tdi(cls, info, root_tree, element, element_id):
        """
        根据公式：

               Ti - LTi
        TDi = -----------
              TGi - LTGi


        Ti:节点 i 的字符串字数
        LTi：节点 i 的带链接的字符串字数
        TGi：节点 i 的标签数
        LTGi：节点 i 的带连接的标签数
        :param element:
        :param element_id:
        :param root_tree:
        :param info:
        :return:
        """
        # if element_id == '/html/body/div[2]/main':
        #     print(1)
        text = cls.get_element_text(info, root_tree, element, element_id)
        ti = len(text)
        a_list = element.xpath('.//a')
        tgi = len(element.xpath('.//*')) or 2  # TODO 默认值待确定
        lti = len(
            ''.join([cls.get_element_text(info, root_tree, a) for a in a_list]))
        ltgi = len(a_list)
        if tgi - ltgi == 0:  # TODO  待验证
            tdi = 0
        else:
            tdi = (ti - lti) / (tgi - ltgi)
        info[element_id]['text'] = text
        info[element_id]['tag'] = str(element.tag)
        info[element_id]['ti'] = ti
        info[element_id]['tgi'] = tgi
        info[element_id]['lti'] = lti
        info[element_id]['ltgi'] = ltgi
        info[element_id]['tdi'] = tdi

    @classmethod
    def calc_element_sbdi(cls, info, element_id):
        """
                Ti - LTi
        SbDi = --------------
                 Sbi + 1

        SbDi: 符号密度
        Sbi：符号数量

        :return:
        """
        _info = info[element_id]
        sbi = 0
        for char in _info['text']:
            if char in content_configs.SYMBOL_LIST:
                sbi += 1
        info[element_id]['sbdi'] = (_info['ti'] - _info['lti']) / (
                sbi + 1) or 1.1

    @classmethod
    def calc_element_p_count(cls, info, element, element_id):
        info[element_id]['p_count'] = len(element.xpath('.//p'))

    @classmethod
    def calc_elements_score(cls, info, element_count):
        for element_id, _info in list(info.items()):
            if _info.get('tdi') is None:
                del info[element_id]
                continue
            score = _info['tdi'] * math.log10(
                _info['p_count'] + 2) * math.log(
                _info['sbdi'])
            info[element_id]['score'] = score

    @classmethod
    def calc_score(cls, num1, num2, mord):
        if mord == 'increase':
            return num1 * num2
        return num1 / num2

    @classmethod
    def update_parent_element_score(cls, info, parent_id, times, func=None,
                                    mord='increase'):
        if not parent_id:
            return
        _info = info.get(parent_id)
        if not _info:
            return
        parent = _info['element']
        if parent is not None:
            if func:
                if func(parent):
                    _info['score'] = cls.calc_score(
                        _info['score'], 2 * times - math.sqrt(times), mord)
                else:
                    _info['score'] = cls.calc_score(
                        _info['score'], times, mord)
            else:
                _info['score'] = cls.calc_score(
                    _info['score'], times, mord)
            if len(parent.getchildren()) == 1:
                return
            cls.update_parent_element_score(
                info, _info.get('parent_id'), math.sqrt(times), func, mord)

    @classmethod
    def update_children_element_score(cls, info, children_ids, times, func=None,
                                      mord='increase'):
        if not children_ids:
            return
        for child_id in children_ids:
            _info = info.get(child_id)
            if not _info:
                continue
            child = _info['element']
            if child is None:
                continue
            if func:
                if func(child):
                    _info['score'] = cls.calc_score(
                        _info['score'], 2 * times - math.sqrt(times), mord)
                else:
                    _info['score'] = cls.calc_score(
                        _info['score'], times, mord)
            else:
                _info['score'] = cls.calc_score(
                    _info['score'], times, mord)
            cls.update_children_element_score(
                info, _info.get('children_ids'), math.sqrt(times), func, mord)

    @classmethod
    def update_siblings_element_score(cls, info, sibling_ids, times, func=None,
                                      mord='increase', children_enabled=True):
        if not sibling_ids:
            return
        for sibling_id in sibling_ids:
            _info = info.get(sibling_id)
            if not _info:
                continue
            sibling = _info['element']
            if sibling is None:
                continue
            if func:
                if func(sibling):
                    _info['score'] = cls.calc_score(
                        _info['score'], 2 * times - math.sqrt(times), mord)
                else:
                    _info['score'] = cls.calc_score(
                        _info['score'], times, mord)
            else:
                _info['score'] = cls.calc_score(
                    _info['score'], times, mord)
            if children_enabled:
                cls.update_children_element_score(
                    info, _info.get('children_ids'), math.sqrt(times), func,
                    mord)

    @classmethod
    def _increase_parent1(cls, element):
        if element.tag in ['p']:
            return True

    @classmethod
    def _decrease_children1(cls, element):
        if element.tag in ['li', 'ul']:
            return True

    @classmethod
    def recalc_elements_score(cls, info, element_count):
        for element_id, _info in info.items():
            element = _info['element']
            import_attrib_value = _info['import_attrib_value']
            score = _info['score']
            if element.tag in ['div', 'p', 'main', 'article']:
                children_tags = []
                for child_id in _info.get('children_ids'):
                    child_info = info.get(child_id)
                    if not child_info:
                        continue
                    child_tag = child_info.get('tag')
                    if not child_tag:
                        continue
                    children_tags.append(child_tag)
                    if child_tag in ['p', 'img', ]:
                        score *= 2
                        cls.update_parent_element_score(
                            info, _info.get('parent_id'), math.sqrt(2),
                            cls._increase_parent1)
                    elif child_tag in ['span', 'strong']:
                        score *= 1.5
                        cls.update_parent_element_score(
                            info, _info.get('parent_id'), math.sqrt(1.5),
                            cls._increase_parent1)
                    elif child_tag in ['a']:
                        score /= 1.5
                        cls.update_parent_element_score(
                            info, _info.get('parent_id'), math.sqrt(1.5),
                            cls._increase_parent1,
                            mord='decrease')
            elif element.tag in ['ul', 'li']:
                score /= 2
                cls.update_children_element_score(
                    info, _info.get('children_ids'), math.sqrt(2),
                    cls._decrease_children1, mord='decrease')
            less_text_child_count = cls.get_less_text_child_count(
                info, _info['children_ids'])
            if less_text_child_count >= 3:
                _times = 2 + math.log(less_text_child_count)
                score /= _times
                cls.update_parent_element_score(
                    info, _info.get('parent_id'), math.sqrt(_times),
                    mord='decrease')
                cls.update_siblings_element_score(
                    info, _info.get('sibling_ids'), math.sqrt(_times),
                    mord='decrease'
                )
            if content_configs.DECREASE_SCORE_ELEMENT_ATTRIB_VALUES_REGEX.search(
                    import_attrib_value):
                _times = 2
                score /= _times
                cls.update_parent_element_score(
                    info, _info.get('parent_id'), math.sqrt(_times),
                    mord='decrease')
                cls.update_siblings_element_score(
                    info, _info.get('sibling_ids'), math.sqrt(_times),
                    mord='decrease'
                )
            if content_configs.INCREASE_SCORE_ELEMENT_ATTRIB_VALUES_REGEX.search(
                    import_attrib_value):
                _times = 2
                score *= _times
                cls.update_children_element_score(
                    info, _info.get('children_ids'), math.sqrt(_times),
                    mord='increase')
            if content_configs.REMOVE_ELEMENT_ATTRIB_VALUES_REGEX.search(
                    import_attrib_value
            ) or content_configs.REMOVE_DISPLAY_NONE_ELEMENT_REGEX.search(
                element.get('style') or ''
            ):
                element.getparent().remove(element)
            _info['score'] = score

    @classmethod
    def handle_content_element(cls, element):
        pass

    @classmethod
    def get_less_text_child_count(cls, info, children_ids, less_count=5):
        count = 0
        for child_id in children_ids:
            child = info.get(child_id)
            if not child:
                continue
            ti = child['ti']
            if not ti:
                continue
            child_tag = child.get('tag')
            if ti <= less_count:
                if child_tag in ['a']:
                    count += 2
                elif child_tag in ['p', 'span', 'strong']:
                    count += 0.5
                else:
                    count += 1
        return count
