# -*- coding:utf-8 -*-
# author: kusen
# email: 1194542196@qq.com
# date: 2023/5/23


HTML_META_XPATH_LIST = [

]

EXTRACT_REGEX_LIST = [
    r'(来源|出处)\s*[：:\|/]\s*(.*?)(\s*[作|<\]）])',
    r'(来源|出处)\s*[：:\|/]\s*(.*?)(\s+)',
    r'(来源|出处)\s*[：:\|/]\s*(.*)($)'
]