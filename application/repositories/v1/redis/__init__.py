"""
Redis Repositories Module for Application
Version: 1.0.0
"""
from itertools import zip_longest


def batcher(iterable, n):
    args = [iter(iterable)] * n
    return zip_longest(*args)
