import shutil
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

here = Path(__file__).parent


class TestPyTest:
    def test_it_collects_tests_correctly(self, tmp_path_factory, monkeypatch):

        directory = tmp_path_factory.mktemp("files")

        monkeypatch.setenv("NOSE_OF_YETI_BLACK_COMPAT", "false")

        shutil.copytree(here / "for_pytest_plugin", directory / "tests")

        want = set(
            dedent(
                """
            tests/test_one.py::test_one
            tests/test_one.py::TestTwo::test_three
            tests/test_one.py::TestTwo::test_four
            tests/test_one.py::TestTwo_Five::test_six
            tests/test_one.py::TestTwo_Seven_Ten::test_eight
            tests/test_one.py::TestTwo_Seven_Ten::test_nine
            tests/test_one.py::TestTwo_Seven_Eleven::test_eight
            tests/test_one.py::TestTwo_Seven_Eleven::test_nine
            tests/test_one.py::TestTwelve::test_thirteen
            tests/test_two.py::TestOne::test_two
            tests/test_two.py::TestOne::test_three
            tests/test_two.py::TestOne::test_four
            tests/test_two.py::TestOne::test_five
            tests/test_two.py::TestOne_Six::test_seven
            tests/test_two.py::TestOne_Eight::test_nine
            tests/test_two.py::TestOne_Ten::test_eleven
            """
            )
            .strip()
            .split("\n")
        )

        with subprocess.Popen(
            [
                sys.executable,
                "-m",
                "pytest",
                str(directory / "tests" / "test_one.py"),
                str(directory / "tests" / "test_two.py"),
                "-v",
                "-o",
                "console_output_style=short",
            ],
            cwd=directory,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        ) as process:
            try:
                process.wait(timeout=5)
            except:
                process.kill()
                raise

            out = process.stdout.read().decode()

            got = set()
            for line in out.split("\n"):
                if "PASSED" in line:
                    got.add(line.split(" ", 1)[0])

            print(out)

            print("WANT:")
            for line in sorted(want):
                print("  ", line)

            print()
            print("GOT:")
            for line in sorted(got):
                print("  ", line)

            assert "16 passed" in out
            assert got == want
