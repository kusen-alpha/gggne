# -*- coding:utf-8 -*-
# author: kusen
# email: 1194542196@qq.com
# date: 2023/5/26


from lxml.html import fromstring, tostring
from lxml.etree import ElementBase

# from lxml.etree import fromstring, tostring

with open('test.html', encoding='utf8') as f:
    data = f.read()


# print(gne.GeneralNewsExtractor().extract(data))

def element_text_count(element):
    count = 0
    text = element.text
    tail = element.tail
    if text:
        count += len(text.strip())
    if tail:
        count += len(tail.strip())
    return count


html = fromstring(data)
html = html.find('body')
x = []
y = []
i = 1
for element in html.iter():
    if not isinstance(element, ElementBase):
        element.getparent().remove(element)
        continue
    if element.tag in ['script', 'style']:
        element.getparent().remove(element)
        continue
    if 'footer' in (element.attrib.get('class') or {}):
        element.getparent().remove(element)
        continue
    x.append(i)
    y.append(element_text_count(element))
    i += 1
import math
import matplotlib.pyplot as plt
print(y)
_y = [_x for _x in y if _x > 0]

m = sum(_y)/len(_y)
print(m)
# y = [_x - m for _x in y]
# x = range(len(y))
# 生成数据

# 创建画布和子图对象
fig, ax = plt.subplots()

# 绘制柱形图
rects = ax.bar(x, y)

# 配置图表属性
ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_title('Title')
plt.show()