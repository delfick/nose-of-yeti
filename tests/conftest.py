import os
import re
import shutil
import tempfile
from contextlib import contextmanager
from io import StringIO
from textwrap import dedent
from tokenize import untokenize

import pytest

from noseOfYeti.tokeniser.tokeniser import WITH_IT_RETURN_TYPE_ENV_NAME


@pytest.fixture(autouse=True)
def remove_with_it_return_type_env(monkeypatch):
    monkeypatch.delenv(WITH_IT_RETURN_TYPE_ENV_NAME, raising=False)


@pytest.fixture()
def a_temp_file():
    @contextmanager
    def a_temp_file(contents):
        tempfle = None
        try:
            tempfle = tempfile.NamedTemporaryFile(delete=False)
            with open(tempfle.name, "w") as fle:
                fle.write(dedent(contents))

            yield tempfle.name
        finally:
            if tempfle:
                if os.path.exists(tempfle.name):
                    os.remove(tempfle.name)

    return a_temp_file


@pytest.fixture()
def a_temp_dir():
    @contextmanager
    def a_temp_dir():
        tempdir = None
        try:
            tempdir = tempfile.mkdtemp()
            yield tempdir
        finally:
            if tempdir:
                if os.path.exists(tempdir):
                    shutil.rmtree(tempdir)

    return a_temp_dir


def pytest_configure():
    @pytest.helpers.register
    def assert_regex_lines(got_lines, want_lines, lstrip=True, rstrip=False):
        __tracebackhide__ = True

        got_lines = dedent(got_lines)
        want_lines = dedent(want_lines)

        if lstrip:
            got_lines = got_lines.lstrip()
            want_lines = want_lines.lstrip()

        if lstrip:
            got_lines = got_lines.rstrip()
            want_lines = want_lines.rstrip()

        print("GOT LINES\n=========")
        print(got_lines)

        print("\n\n\nWANT LINES\n==========")
        print(want_lines)

        for i, (wl, gl) in enumerate(zip(want_lines.split("\n"), got_lines.split("\n"))):
            try:
                m = re.match(wl, gl)
            except re.error as error:
                pytest.fail(f"Failed to turn line into a regex\nCONVERTING: {wl}\nERROR: {error}")

            if not m:
                pytest.fail(f"line {i} does not match. Wanted:\n{wl}\n\nGot:\n{gl}")

    @pytest.helpers.register
    def assert_lines(got_lines, want_lines, lstrip=True, rstrip=False, rstrip_got_lines=True):
        __tracebackhide__ = True

        got_lines = dedent(got_lines)
        want_lines = dedent(want_lines)

        if lstrip:
            got_lines = got_lines.lstrip()
            want_lines = want_lines.lstrip()

        if lstrip:
            got_lines = got_lines.rstrip()
            want_lines = want_lines.rstrip()

        print("GOT LINES\n=========")
        print(got_lines)

        print("\n\n\nWANT LINES\n==========")
        print(want_lines)

        for i, (wl, gl) in enumerate(zip(want_lines.split("\n"), got_lines.split("\n"))):
            if rstrip_got_lines:
                gl = gl.rstrip()
            if wl != gl:
                pytest.fail(f"line {i} does not match. Wanted:\n{wl}\n\nGot:\n{gl}")

    @pytest.helpers.register
    def assert_conversion(
        original, want_lines, *, tokeniser=None, regex=False, lstrip=True, rstrip=False
    ):
        __tracebackhide__ = True

        from noseOfYeti.tokeniser import Tokeniser

        original = dedent(original)
        if lstrip:
            original = original.lstrip()
        if rstrip:
            original = original.rstrip()

        if tokeniser is None:
            tokeniser = {}

        for give_return_types, ret in ((False, ""), (True, "->None ")):
            orig = original.replace("$RET", ret)
            want = want_lines.replace("$RET", ret)

            if give_return_types:
                kwargs = {**tokeniser, "with_it_return_type": True}
            else:
                kwargs = {**tokeniser, "with_it_return_type": False}

            s = StringIO(orig)
            tok = Tokeniser(**kwargs)
            got_lines = untokenize(tok.translate(s.readline))

            if regex:
                pytest.helpers.assert_regex_lines(got_lines, want, lstrip=lstrip, rstrip=rstrip)
            else:
                pytest.helpers.assert_lines(got_lines, want, lstrip=lstrip, rstrip=rstrip)

    @pytest.helpers.register
    def assert_example(example, convert_to_tabs=False, **kwargs):
        __tracebackhide__ = True

        original, desired = example
        if convert_to_tabs:
            original = original.replace("    ", "\t")
            desired = desired.replace("    ", "\t")

        pytest.helpers.assert_conversion(original, desired, tokeniser=kwargs)
