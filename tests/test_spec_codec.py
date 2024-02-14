import fnmatch
import os
import subprocess
import sys
from textwrap import dedent
from unittest import mock

import pytest

from noseOfYeti.tokeniser.spec_codec import Tokeniser, TokeniserCodec

this_dir = os.path.dirname(__file__)
example_dir = os.path.join(this_dir, "..", "example")


def assert_run_subprocess(cmd, expected_output, status=0, **kwargs):
    __tracebackhide__ = True

    # necessary so that tests pass on windows
    env = os.environ.copy()
    env.update(kwargs.get("env", {}))
    kwargs["env"] = env

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **kwargs)
    process.wait()

    output = process.stdout.read().decode("utf8").strip().replace("\r\n", "\n")

    print("the process output:")
    print("~" * 80)
    print(output)
    print("~" * 80)

    assert process.returncode == status

    if expected_output is not None:
        pytest.helpers.assert_regex_lines(output, expected_output)

    return output


def assert_glob_lines(got, expect):
    message = [line.strip() for line in got.strip().replace("\r\n", "\n").split("\n")]
    want = [line.strip() for line in expect.strip().split("\n")]

    print("GOT >>" + "=" * 74)
    print()
    print("\n".join(message))
    print()
    print("WANT >>" + "-" * 73)
    print()
    print("\n".join(want))

    count = 1
    while want:
        line = want[0]
        if not message:
            assert False, f"Ran out of lines, stopped at [{count}] '{want[0]}'"

        if message[0] == line or fnmatch.fnmatch(message[0], line):
            count += 1
            want.pop(0)

        message.pop(0)

    if want:
        assert False, f"Didn't match all the lines, stopped at [{count}] '{want[0]}'"


class Test_RegisteringCodec:
    @pytest.fixture()
    def directory(self, tmp_path_factory):
        directory = tmp_path_factory.mktemp("registering_codec")

        with open(directory / "test_code.py", "w") as fle:
            fle.write(
                dedent(
                    """
            # coding: spec

            describe "blah":
                it "should totally work":
                    1 + 1 |should| equal_to(2)

            if hasattr(TestBlah, 'test_should_totally_work'):
                print("test_should_totally_work")
            """
                ).strip()
            )

        with open(directory / "registerer.py", "w") as fle:
            fle.write(
                dedent(
                    """
            import codecs

            try:
                codecs.lookup("spec")
            except LookupError:
                pass
            else:
                assert False, "A spec was already registered!"

            from noseOfYeti.tokeniser import register
            register(transform=True)
            """
                ).strip()
            )

        return directory

    def test_not_registering_codec_leads_to_error(self, directory):
        output = assert_run_subprocess(
            [sys.executable, "-c", "import test_code"],
            expected_output=None,
            cwd=directory,
            env={"NOSE_OF_YETI_BLACK_COMPAT": "false"},
            status=1,
        )
        expected_output = "SyntaxError: [Uu]nknown encoding: spec"
        pytest.helpers.assert_regex_lines(output.split("\n")[-1], expected_output)

    def test_registering_codec_doesnt_lead_to_error(self, directory):
        assert_run_subprocess(
            [sys.executable, "-c", "import registerer; import test_code"],
            expected_output="test_should_totally_work",
            cwd=directory,
            env={"NOSE_OF_YETI_BLACK_COMPAT": "false"},
            status=0,
        )

    def test_can_correctly_translate_file(self):
        with open(os.path.join(example_dir, "test.py")) as fle:
            original = fle.read()
        with open(os.path.join(example_dir, "converted.test.py")) as fle:
            want = fle.read()

        after = TokeniserCodec(Tokeniser()).translate(original)
        pytest.helpers.assert_lines(after, want)

    def test_it_shows_errors(self):
        get_codec = mock.Mock(name="get_codec")
        readline = mock.Mock(name="readline")
        tokeniser = mock.Mock(name="tokeniser")
        tokeniser.translate.side_effect = Exception("NOPE")

        with mock.patch.object(TokeniserCodec, "get_codec", get_codec):
            codec = TokeniserCodec(tokeniser)

            got = codec.dealwith(readline)
            tokeniser.translate.assert_called_once_with(readline, [])

            expect = dedent(
                r'''
                msg = r"""
                Traceback (most recent call last):
                File "*noseOfYeti*tokeniser*spec_codec.py", line *, in dealwith
                Exception: NOPE
                """
                raise Exception(f"--- internal spec codec error --- \n{msg}")
                '''
            )

            assert_glob_lines(got, expect)

            with pytest.raises(Exception) as excinfo:
                exec(got)

            assert excinfo.exconly().startswith("Exception: --- internal spec codec error ---")
