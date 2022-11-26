import shutil
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

import pytest

from noseOfYeti.plugins.black_compat import is_supported_black_version

try:
    import black

    if not is_supported_black_version():
        pytestmark = pytest.mark.skip(
            f"Currently installed black is an unsupported version {black.__version__}"
        )
except ImportError:
    pytestmark = pytest.mark.skip("black is not current installed")

here = Path(__file__).parent
test_dir = here / "for_formatting_and_pylama"


class TestBlackFormatting:
    def test_it_formats(self, tmp_path_factory, monkeypatch):

        from black.cache import CACHE_DIR

        if CACHE_DIR.exists():
            for fle in CACHE_DIR.iterdir():
                if "noy" in fle.name:
                    fle.unlink()

        directory = tmp_path_factory.mktemp("files")

        monkeypatch.setenv("PYTHONPATH", str(directory))
        monkeypatch.setenv("NOSE_OF_YETI_BLACK_COMPAT", "true")

        with open(directory / "sitecustomize.py", "w") as fle:
            fle.write(
                dedent(
                    """
            import site
            import os
            site.addsitedir(os.getcwd())
            """
                )
            )

        shutil.copy(test_dir / "unformatted_spec.py", directory / "unformatted_spec.py")
        shutil.copy(test_dir / "unformatted_normal.py", directory / "unformatted_normal.py")

        path = Path(__import__("noseOfYeti").__file__).parent / "black" / "noy_black.pth"
        shutil.copy(path, directory)

        subprocess.check_call([sys.executable, "-m", "black", str(directory)], cwd=directory)

        with open(directory / "unformatted_spec.py") as spec_result, open(
            test_dir / "formatted_spec.py"
        ) as spec_want:
            assert spec_result.read() == spec_want.read()

        with open(directory / "unformatted_normal.py") as normal_result, open(
            test_dir / "formatted_normal.py"
        ) as normal_want:
            assert normal_result.read() == normal_want.read()
