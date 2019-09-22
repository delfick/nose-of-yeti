'''
Tests to make sure registering the spec codec actually works
'''

from noseOfYeti.tokeniser.spec_codec import TokeniserCodec

from should_dsl import should
from textwrap import dedent
import subprocess
import fudge
import sys
import os

from .helpers import a_temp_file, a_temp_dir

# Silencing code checker about should_dsl matchers
be = None
equal_to = None
start_with = None

init_codez = """
from noseOfYeti.tokeniser.spec_codec import register_from_options
register_from_options()
"""

example_specd_tests = """
# coding: spec

describe "blah":
    it "should totally work":
        1 + 1 |should| equal_to(2)


if hasattr(TestBlah, 'test_should_totally_work'):
    print("test_should_totally_work")
""".strip()

class Test_RegisteringCodec(object):
    def test_not_registering_codec_leads_to_error(self):
        with a_temp_file(example_specd_tests) as filename:
            process = subprocess.Popen([sys.executable, filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            process.wait()
            process.returncode |should| be(1)

            expected_output = 'File "{}", line 1\nSyntaxError: encoding problem'.format(filename)
            process.stdout.read().decode('utf8').strip() |should| start_with(expected_output)

    def test_registering_codec_doesnt_lead_to_error(self):
        with a_temp_dir() as tempdir:
            with open(os.path.join(tempdir, "codez.py"), 'w') as fle:
                fle.write(example_specd_tests)

            with open(os.path.join(tempdir, "spec_setup.py"), 'w') as fle:
                fle.write(init_codez)

            filename = os.path.join(tempdir, "script.py")
            with open(filename, 'w') as fle:
                fle.write("import spec_setup; import codez")

            process = subprocess.Popen([sys.executable, filename], cwd=tempdir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            process.wait()
            if process.returncode != 0:
                print(process.stdout.read().decode('utf8'))
            process.returncode |should| be(0)

            expected_output = 'test_should_totally_work'
            process.stdout.read().decode('utf8').strip() |should| equal_to(expected_output)

    @fudge.patch("noseOfYeti.tokeniser.spec_codec.TokeniserCodec.get_codec")
    def test_it_shows_errors(self, fake_get_codec):
        exc = Exception("WAT")
        fake_get_codec.is_a_stub()
        readline = fudge.Fake("readline")
        tokeniser = (fudge.Fake("tokeniser")
            .expects("translate").with_args(readline, []).raises(exc)
            )
        tok = TokeniserCodec(tokeniser)

        data = tok.dealwith(readline)

        expected = dedent(r'''
        msg = """
        Traceback \(most recent call last\):
        File ".+noseOfYeti/tokeniser/spec_codec.py", line 123, in dealwith
            self.tokeniser.translate\(readline, data, \*\*kwargs\)
        File ".+fudge/__init__.py", line 365, in __call__
            raise self.exception_to_raise
        Exception: WAT
        """
        raise Exception\('--- internal spec codec error --- \\n\{0\}'.format\(msg\)\)
        ''')
        data |should| match_regex_lines(expected)

        try:
            exec(data)
            assert False, "Expected an exception"
        except Exception as error:
            str(error) |should| start_with("--- internal spec codec error ---")
