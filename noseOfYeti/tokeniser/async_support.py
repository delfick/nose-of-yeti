"""
A helper module to access the superclass'
setUp() and tearDown() methods of generated
test classes.

NB: We pull this into it's own module to:
1) not repeat these methods in all generated modules
2) avoid errors when inspecting the stack (e.g. in flexmock)
"""

from functools import wraps
import asyncio

async def async_noy_sup_setUp(sup):
    if hasattr(sup, "setup"):
        res = sup.setup()
        if res and asyncio.iscoroutine(res):
            return await res
        else:
            return res

    if hasattr(sup, "setUp"):
        res = sup.setUp()
        if res and asyncio.iscoroutine(res):
            return await res
        else:
            return res

async def async_noy_sup_tearDown(sup):
    if hasattr(sup, "teardown"):
        res = sup.teardown()
        if res and asyncio.iscoroutine(res):
            return await res
        else:
            return res

    if hasattr(sup, "tearDown"):
        res = sup.tearDown()
        if res and asyncio.iscoroutine(res):
            return await res
        else:
            return res

def async_noy_wrap_setUp(kls, func):
    @wraps(func)
    async def wrapped(self, *args, **kwargs):
        sup = super(kls, self)
        await async_noy_sup_setUp(sup)
        return await func(self, *args, **kwargs)
    return wrapped

def async_noy_wrap_tearDown(kls, func):
    @wraps(func)
    async def wrapped(self, *args, **kwargs):
        sup = super(kls, self)
        await async_noy_sup_tearDown(sup)
        return await func(self, *args, **kwargs)
    return wrapped
