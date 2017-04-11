"""
A helper module to access the superclass'
setUp() and tearDown() methods of generated
test classes.

NB: We pull this into it's own module to:
1) not repeat these methods in all generated modules
2) avoid errors when inspecting the stack (e.g. in flexmock)
"""

from functools import wraps

async def async_noy_sup_setUp(sup):
    if hasattr(sup, "setup"):
        return await sup.setup()

    if hasattr(sup, "setUp"):
        return await sup.setUp()

async def async_noy_sup_tearDown(sup):
    if hasattr(sup, "teardown"):
        return await sup.teardown()

    if hasattr(sup, "tearDown"):
        return await sup.tearDown()

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
