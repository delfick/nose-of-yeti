import os

import pytest


@pytest.hookimpl()
def pytest_ignore_collect(collection_path, path, config):
    return "INNER_PYTEST_RUN" not in os.environ
