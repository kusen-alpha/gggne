# -*- coding:utf-8 -*-
# author: kusen
# email: 1194542196@qq.com
# date: 2023/5/23


HTML_META_XPATH_LIST = [
    r'//meta[@name="author"]/@content',
    r'//meta[@property="author"]/@content',

    r'//meta[contains(@property, "creator")]/@content',
    r'//meta[contains(@name, "creator")]/@content',
    r'//meta[contains(@property, "lead:author")]/@content',
    r'//meta[contains(@name, "lead:author")]/@content',
    r'//meta[contains(@property, "author")]/@content',
    r'//meta[contains(@name, "author")]/@content',
    r'//meta[contains(@property, "writer")]/@content',
    r'//meta[contains(@name, "writer")]/@content',
    r'//meta[contains(@property, "publisher")]/@content',
    r'//meta[contains(@name, "publisher")]/@content',
]

EXTRACT_REGEX_LIST = [
    r'(作者|编辑|记者|责编|原创|撰文|writer|发布者)\s*[：:\|/]\s*(.*?)(\s+[】|<来\]])',
    r'(作者|编辑|记者|责编|原创|撰文|writer|发布者)\s*[：:\|/]\s*(.*?)(\s+)',
    r'(作者|编辑|记者|责编|原创|撰文|writer|发布者)\s*[：:\|/]\s*(.*)($)'
]

ELEMENT_ATTRIB_LIST = ['writer', 'user-name']