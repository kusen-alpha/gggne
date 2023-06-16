# -*- coding:utf-8 -*-
# author: kusen
# email: 1194542196@qq.com
# date: 2023/5/23


HTML_META_XPATH_LIST = [
    '//meta[contains(@property, "published_time")]/@content',
    '//meta[contains(@property, "published_at")]/@content',
    '//meta[contains(@property, "published")]/@content',
    '//meta[contains(@property, "Published")]/@content',
    '//meta[contains(@property, "PublicationDate")]/@content',
    '//meta[contains(@property, "publication_date")]/@content',
    '//meta[contains(@property, "PublishDate")]/@content',
    '//meta[contains(@property, "publishdate")]/@content',
    '//meta[contains(@property, "pubtime")]/@content',
    '//meta[contains(@property, "pubdate")]/@content',
    '//meta[contains(@property, "modified_time")]/@content',
    '//meta[contains(@name, "published_time")]/@content',
    '//meta[contains(@name, "published_at")]/@content',
    '//meta[contains(@name, "published")]/@content',
    '//meta[contains(@name, "Published")]/@content',
    '//meta[contains(@name, "PublicationDate")]/@content',
    '//meta[contains(@name, "publication_date")]/@content',
    '//meta[contains(@name, "PublishDate")]/@content',
    '//meta[contains(@name, "publishdate")]/@content',
    '//meta[contains(@name, "pubtime")]/@content',
    '//meta[contains(@name, "pubdate")]/@content',
    '//meta[contains(@name, "modified_time")]/@content',
    '//meta[contains(@itemprop, "published_time")]/@content',
    '//meta[contains(@itemprop, "published_at")]/@content',
    '//meta[contains(@itemprop, "published")]/@content',
    '//meta[contains(@itemprop, "Published")]/@content',
    '//meta[contains(@itemprop, "PublicationDate")]/@content',
    '//meta[contains(@itemprop, "publication_date")]/@content',
    '//meta[contains(@itemprop, "PublishDate")]/@content',
    '//meta[contains(@itemprop, "publishdate")]/@content',
    '//meta[contains(@itemprop, "pubtime")]/@content',
    '//meta[contains(@itemprop, "pubdate")]/@content',
    '//meta[contains(@itemprop, "modified_time")]/@content',
]