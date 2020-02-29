"""
A helper module to access the superclass'
setUp() and tearDown() methods of generated
test classes.
"""

import asyncio


class TestSetup:
    def __init__(self, sup):
        self.sup = sup

    @property
    def setup(self):
        if hasattr(self.sup, "setup"):
            return self.sup.setup
        if hasattr(self.sup, "setUp"):
            return self.sup.setUp

    @property
    def teardown(self):
        if hasattr(self.sup, "teardown"):
            return self.sup.teardown
        if hasattr(self.sup, "tearDown"):
            return self.sup.tearDown

    def sync_before_each(self):
        setup = self.setup
        if setup:
            return setup()

    def sync_after_each(self):
        teardown = self.teardown
        if teardown:
            return teardown()

    async def async_before_each(self):
        res = self.sync_before_each()
        if res and asyncio.iscoroutine(res):
            return await res
        else:
            return res

    async def async_after_each(self):
        res = self.sync_after_each()
        if res and asyncio.iscoroutine(res):
            return await res
        else:
            return res
