"""
A helper module to access the superclass'
setUp() and tearDown() methods of generated
test classes.

NB: We pull this into it's own module to:
1) not repeat these methods in all generated modules
2) avoid errors when inspecting the stack (e.g. in flexmock)
"""

from functools import wraps

def noy_sup_setUp(sup):
    if hasattr(sup, "setup"):
        return sup.setup()

    if hasattr(sup, "setUp"):
        return sup.setUp()

def noy_sup_tearDown(sup):
    if hasattr(sup, "teardown"):
        return sup.teardown()

    if hasattr(sup, "tearDown"):
        return sup.tearDown()

def noy_wrap_setUp(kls, func):
    @wraps(func)
    def wrapped(self, *args, **kwargs):
        sup = super(kls, self)
        noy_sup_setUp(sup)
        return func(self, *args, **kwargs)
    return wrapped

def noy_wrap_tearDown(kls, func):
    @wraps(func)
    def wrapped(self, *args, **kwargs):
        sup = super(kls, self)
        noy_sup_tearDown(sup)
        return func(self, *args, **kwargs)
    return wrapped
