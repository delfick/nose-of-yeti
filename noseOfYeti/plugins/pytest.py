"""
Modified pytest discovery classes.

This is so you can use noseOfYeti to have nested describes without running the
same tests multiple times.

It achieves this by making classes have a ModifiedInstance object that discards
any collected tests that aren't on that class.
"""
from noseOfYeti.tokeniser.spec_codec import register

from _pytest.unittest import UnitTestCase
from functools import partial
from unittest import mock
import inspect
import pytest


def pytest_configure():
    register()


@pytest.hookimpl(hookwrapper=True)
def pytest_pycollect_makeitem(collector, name, obj):
    """Make sure we can have nested noseOfYeti describes"""
    outcome = yield
    res = outcome.get_result()

    if res is None:
        return

    if not hasattr(res, "obj"):
        is_noy_on_obj = getattr(obj, "is_noy_spec", False)
        is_noy_on_class = getattr(obj.__class__, "is_noy_spec", False)
        if not is_noy_on_obj and not is_noy_on_class:
            return

    original_item_collect = res.collect

    if isinstance(res, UnitTestCase):
        original_item_collect = res.collect

        def collect():
            yield from filter_collection(original_item_collect(), res.obj)

        mock.patch.object(res, "collect", collect).start()
    else:

        def collect():
            got = original_item_collect()
            for g in got:
                original_collect = g.collect
                mock.patch.object(
                    g, "collect", partial(modified_class_collect, g, original_collect)
                ).start()
            return got

        mock.patch.object(res, "collect", collect).start()


def modified_class_collect(instance, original_collect):
    instance.session._fixturemanager.parsefactories(instance)
    yield from filter_collection(original_collect(), instance.obj)


def filter_collection(collected, obj):
    for thing in collected:
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
