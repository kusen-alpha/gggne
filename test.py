# import json
#
# from gggne.details import extract
# from lxml import etree
#
# # result = download_and_extract('https://www.jnnews.tv/p/976927.html', encoding='auto')
# # print(json.dumps(result, ensure_ascii=False))
#
#
# with open('test.html', encoding='utf8') as f:
#     text = f.read()
# html = etree.HTML(text)
# result = extract(text, html)
# print(json.dumps(result, ensure_ascii=False))
# print(result['content'])
import json
import math
from urllib.parse import urljoin
from urllib.parse import urlparse

from gggne.section import download_and_extract
from gggne.details_list import download_and_extract

r = download_and_extract('https://news.sina.com.cn/', False, encoding='utf-8')
print(json.dumps(r, ensure_ascii=False))
