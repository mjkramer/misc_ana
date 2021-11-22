#!/usr/bin/env python3

from contextlib import contextmanager

@contextmanager
def deleter(obj):
    try:
        yield obj
    finally:
        del obj
