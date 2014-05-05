'''
Tests to make sure registering the spec codec actually works
'''
from should_dsl import should
import subprocess
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
