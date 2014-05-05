from contextlib import contextmanager
from textwrap import dedent
import tempfile
import shutil
import os

@contextmanager
def a_temp_file(contents):
    tempfle = None
    try:
        tempfle = tempfile.NamedTemporaryFile(delete=False)
        with open(tempfle.name, 'w') as fle:
            fle.write(dedent(contents))

        yield tempfle.name
    finally:
        if tempfle:
            if os.path.exists(tempfle.name):
                os.remove(tempfle.name)

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

