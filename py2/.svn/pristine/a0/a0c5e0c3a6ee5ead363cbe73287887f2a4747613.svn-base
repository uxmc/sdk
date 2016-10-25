# encoding: utf-8
from __future__ import absolute_import
import time

__author__ = u'yonka'


def schedule_task(fn, initial_delay=0, period=0, repeat=1):
    u"""
    @:param fn should handle exception itself
    @:param repeat <= 0 means infinite repeat
    """

    def _fn(*args, **kwargs):
        cnt = 0
        if initial_delay > 0:
            time.sleep(initial_delay)
        while repeat <= 0 or repeat > cnt:
            cnt += 1
            _continue = fn(*args, **kwargs)
            if not _continue:
                break
            if period > 0:
                time.sleep(period)

    return _fn


def timestamp():
    return int(time.time() * 1000)


def is_stock(symbol):
    if symbol.split(".")[0] == "SHSE" or symbol.split(".")[0] == "SZSE":
        return True
    else:
        return False
