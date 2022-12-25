# coding: spec

import shutil
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

import pytest

try:
    __import__("pylama")
except ImportError:
    pytestmark = pytest.mark.skip("pylama is not current installed")

here = Path(__file__).parent
test_dir = here / "for_formatting_and_pylama"


class TestPylama:
    @pytest.fixture(params=(False, True), ids=["Without black compat", "With black compat"])
    def directory(self, request, tmp_path_factory, monkeypatch):
        directory = tmp_path_factory.mktemp("files")

        monkeypatch.setenv("PYTHONPATH", str(directory))
        monkeypatch.setenv("NOSE_OF_YETI_BLACK_COMPAT", str(request.param).lower())

        with open(directory / "pylama.ini", "w") as fle:
            fle.write(
                dedent(
                    """
            [pylama]
            linters = pylama_noy,mccabe,pycodestyle,pyflakes
            ignore = E225,E202,E211,E231,E226,W292,W291,E251,E122,E501,E701,E227,E305,E128,E228,E203,E261
            """
                )
            )

        if request.param:
            path = Path(__import__("noseOfYeti").__file__).parent / "black" / "noy_black.pth"
            shutil.copy(path, directory)

            with open(directory / "sitecustomize.py ", "w") as fle:
                fle.write(
                    dedent(
                        """
            import site
            import os
            site.addsitedir(os.getcwd())
            """
                    )
                )

        yield directory

    def test_it_lints_when_there_is_black_compat(self, directory):
        shutil.copy(test_dir / "formatted_spec.py", directory / "formatted_spec.py")
        shutil.copy(test_dir / "formatted_normal.py", directory / "formatted_normal.py")

        subprocess.check_call([sys.executable, "-m", "pylama", str(directory)], cwd=directory)

    def test_it_finds_problems(self, directory):
        shutil.copy(test_dir / "failing_pylama_spec.py", directory / "formatted_spec.py")

        p = subprocess.run(
            [sys.executable, "-m", "pylama", str(directory)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=directory,
            check=False,
        )

        assert p.returncode == 1

        assert (
            p.stdout.decode().strip().replace("\r\n", "\n")
            == dedent(
                """
            formatted_spec.py:3:1 W0611 'sys' imported but unused [pyflakes]
            formatted_spec.py:5:1 E302 expected 2 blank lines, found 1 [pycodestyle]
            formatted_spec.py:7:9 W0612 local variable 'a' is assigned to but never used [pyflakes]
            formatted_spec.py:8:9 E0602 undefined name 'stuff' [pyflakes]
            """
            ).strip()
        )
