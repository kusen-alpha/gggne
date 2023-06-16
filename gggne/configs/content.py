# -*- coding:utf-8 -*-
# author: kusen
# email: 1194542196@qq.com
# date: 2023/5/30


import re

EXCLUDE_EMPTY_ELEMENT_TAGS = ['a', 'img', 'video', 'audio']
REMOVE_ELEMENT_ATTRIB_VALUES = ['footer']
REMOVE_UNLESS_TAGS = ['style', 'script', 'link', 'iframe', 'source', 'header',
                      'blockquote', 'footer']
SYMBOL_LIST = set('''！，。？、；：“”‘’《》%（）,.?:;'"!%()''')
DECREASE_SCORE_ELEMENT_ATTRIB_VALUES_REGEX = re.compile(
    'foot|bottom|copyright|description', re.I)
INCREASE_SCORE_ELEMENT_ATTRIB_VALUES_REGEX = re.compile(
    'article|content|main|post|details', re.I)
REMOVE_ELEMENT_ATTRIB_VALUES_REGEX = re.compile(
    'notice', re.I)  # 有些网站用了标签用了seo双份标签同样数据 |seo-|-seo
REMOVE_DISPLAY_NONE_ELEMENT_REGEX = re.compile(r'^display\s*:\s*none\s*;?$')