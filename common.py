import copy
import os
import time
from contextlib import contextmanager

import moment
import numpy as np
import requests
from PIL import Image

from conf import conf
from log import error, info, success


@contextmanager
def checkTimes(level=3, msg=" "):
    timeStart = time.time()
    yield
    success(f"{msg}cost times: {round(time.time()-timeStart,level)}s")


def error_log(default=None, need_raise=False):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error(f"[{func.__name__}]: {e}")
                if need_raise:
                    raise e
                return default

        return wrapper

    return decorator


def addsucess():
    conf.status["success"] += 1
    conf.status["fetching"] -= 1


def addfailed():
    conf.status["failed"] += 1
    conf.status["fetching"] -= 1


def addtotal():
    conf.status["total"] += 1


def addupdate():
    conf.status["fetching"] += 1


def checkPath(path):
    return os.path.exists(path)


def initPath(path):
    if not checkPath(path):
        os.makedirs(path)


def make_chunk(datas, length=512):
    data = True
    while data:
        chunk = []
        while len(chunk) < length:
            try:
                data = next(datas)
                chunk.append(data)
            except Exception as e:
                data = None
                break
        yield chunk


def read_stopwords(path="stopwords.txt"):
    if path and os.path.exists(path):
        with open(path, "r", encoding="utf8") as file:
            return map(lambda item: item.strip(), file.readlines())
    else:
        error(f"stopwords [{path}] not found!")
        return []


@error_log()
def get_pic_array(url, path):
    resp = requests.get(url)
    success(f"GET PIC From: {url}")
    with open(path, "wb") as f:
        f.write(resp.content)
    new_path = conf.words_background
    if new_path:
        if os.path.exists(new_path):
            path = new_path
        else:
            error(f"pic [{new_path}] not found!")
    return np.array(Image.open(path))
