"""
Modified pytest discovery classes.

This is so you can use noseOfYeti to have nested describes without running the
same tests multiple times.

It achieves this by making classes have a ModifiedInstance object that discards
any collected tests that aren't on that class.
"""
from noseOfYeti.tokeniser.spec_codec import register_from_options

from functools import partial
from unittest import mock
import inspect
import pytest

def pytest_configure():
    register_from_options()

@pytest.hookimpl(hookwrapper=True)
def pytest_pycollect_makeitem(collector, name, obj):
    """Make sure we can have nested noseOfYeti describes"""
    outcome = yield
    res = outcome.get_result()
    if res is not None:
        try:
            isclass = inspect.isclass(res.obj)
        except Exception:
            isclass = False

        if not isclass:
            return res

        outcome.force_result(ModifiedClass(name, parent=collector))

def modified_collect(instance, original_collect):
    instance.session._fixturemanager.parsefactories(instance)
    collected = original_collect()
    modified_collected = []
    for thing in collected:
        if not isinstance(thing, pytest.Function):
            modified_collected.append(thing)
            continue

        is_noy = getattr(instance.obj.__class__, "is_noy_spec", False)
        if not is_noy or thing.obj.__name__ in instance.obj.__class__.__dict__:
            modified_collected.append(thing)

    return modified_collected

class ModifiedClass(pytest.Class):
    def collect(self):
        got = super().collect()
        for g in got:
            original_collect = g.collect
            mock.patch.object(g, "collect", partial(modified_collect, g, original_collect)).start()
        return got
