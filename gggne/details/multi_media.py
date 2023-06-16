# -*- coding:utf-8 -*-
# author: kusen
# email: 1194542196@qq.com
# date: 2023/5/30


import re
from urllib.parse import urljoin

import jinja2

from gggne import utils

ENV = jinja2.Environment()

IMAGE_TAG = "\n{ IMAGE:{{ images|index('%s') }} }\n"
VIDEO_TAG = "\n{ VIDEO:{{ images|index('%s') }} }\n"
AUDIO_TAG = "\n{ AUDIO:{{ images|index('%s') }} }\n"
FILE_TAG = "\n{ FILE:{{ images|index('%s') }} }\n"
TAG_START_INDEX = 0


def index(seq, item):
    try:
        return seq.index(item) + TAG_START_INDEX
    except ValueError:
        return None


ENV.filters['index'] = index


class MultiMediaExtract:
    @classmethod
    def extract(cls, element, element_text='', image_config=None,
                video_config=None, audio_config=None,
                file_config=None, mark=True):
        if not image_config:
            image_config = {}
        if not video_config:
            video_config = {}
        if not audio_config:
            audio_config = {}
        if not file_config:
            file_config = {}
        info = {}
        images = {}
        videos = {}
        audios = {}
        files = {}
        for ele in element.iter():
            ele_id = str(id(ele))
            info[ele_id] = {
                'element': ele,
                'done': False
            }
            ele_tag = ele.tag
            if ele_tag in ['style', 'script']:
                ele.getparent().remove(ele)
                continue
            if ele_tag in ['img']:
                cls.handle_image_element(info, ele, ele_id, images, mark)
            elif ele_tag in ['video']:
                cls.handle_video_element(info, ele, ele_id, videos, mark)
            elif ele_tag in ['audio']:
                cls.handle_audio_element(info, ele, ele_id, audios, mark)
            else:
                continue
        content = ENV.from_string('\n'.join(element.xpath('.//text()')).strip())
        content = content.render({
            "images": list(images.keys()),
            "videos": list(videos.keys()),
            "audios": list(audios.keys()),
            "files": list(files.keys()),
        })
        content = cls.handle_content_text(content)
        return {
            'content': content.strip(),
            'images': list(images.values()),
            'videos': list(videos.values()),
            'audios': list(audios.values()),
            'files': list(files.values()),
        }

    @classmethod
    def handle_content_text(cls, content):
        content = re.sub(r"(\r?\n\s+\n?)+", r"\n", content, re.M | re.S | re.I)
        content = re.sub(r"(\n\s+)", r"\n", content, re.M | re.S | re.I)
        return content

    @classmethod
    def handle_multi_media_element(cls, info, element, element_id, src,
                                   container, tag, mark):
        if not src:
            return
        src = urljoin(element.base, src)
        hash_src = utils.md5(src)
        container[hash_src] = src
        info[element_id]['done'] = True
        if mark:
            text = element.text
            render_text = tag % hash_src
            text = text + render_text if text else render_text
            element.text = text

    @classmethod
    def handle_image_element(cls, info, element, element_id, images, mark):
        src = element.get('src')
        cls.handle_multi_media_element(
            info, element, element_id, src, images, tag=IMAGE_TAG, mark=mark)

    @classmethod
    def handle_video_element(cls, info, element, element_id, videos, mark):
        src = element.get('src')
        cls.handle_multi_media_element(
            info, element, element_id, src, videos, tag=VIDEO_TAG, mark=mark)

    @classmethod
    def handle_audio_element(cls, info, element, element_id, audios, mark):
        src = element.get('src')
        cls.handle_multi_media_element(
            info, element, element_id, src, audios, tag=AUDIO_TAG, mark=mark)

    @classmethod
    def handle_file_element(cls, info, element, element_id, files, mark):
        src = element.get('src')
        cls.handle_multi_media_element(
            info, element, element_id, src, files, tag=FILE_TAG, mark=mark)
