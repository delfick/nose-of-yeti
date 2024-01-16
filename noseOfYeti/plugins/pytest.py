"""
Modified pytest discovery classes.

This is so you can use noseOfYeti to have nested describes without running the
same tests multiple times.
"""
import inspect
from unittest import mock

import pytest
from _pytest.unittest import UnitTestCase

from noseOfYeti.tokeniser.spec_codec import register

pytest_has_instance_class = int(pytest.__version__.split(".")[0]) < 7


def pytest_configure():
    register(transform=True)


def change_item(res, obj):
    original_item_collect = res.collect

    if isinstance(res, UnitTestCase):

        def collect():
            yield from filter_collection(original_item_collect(), obj)

    else:

        def collect():
            res.session._fixturemanager.parsefactories(res)
            yield from filter_collection(original_item_collect(), obj)

    mock.patch.object(res, "collect", collect).start()


@pytest.hookimpl(hookwrapper=True)
def pytest_pycollect_makeitem(collector, name, obj):
    """Make sure we can have nested noseOfYeti describes"""
    outcome = yield
    res = outcome.get_result()

    if not isinstance(res, pytest.Class):
        return

    change_item(res, obj)


def filter_collection(collected, obj):
    for thing in collected:
        if pytest_has_instance_class and isinstance(thing, pytest.Instance):
            if getattr(thing.obj, "is_noy_spec", False):
                change_item(thing, thing.obj)

        if not isinstance(thing, pytest.Function):
            yield thing
            continue

        try:
            isclass = inspect.isclass(obj)
            if not isclass:
                obj = obj.__class__
        except Exception:
            pass

        if obj.__dict__.get("__only_run_tests_in_children__"):
            # Only run these tests in the children, not in this class itself
            continue

        if thing.obj.__name__ in obj.__dict__:
            yield thing
        else:
            method_passed_down = any(
                thing.obj.__name__ in superkls.__dict__
                and getattr(superkls, "__only_run_tests_in_children__", False)
                for superkls in obj.__bases__
            )
            if method_passed_down:
                yield thing
