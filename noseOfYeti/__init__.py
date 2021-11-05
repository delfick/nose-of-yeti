"""pytest-cov: avoid already-imported warning: PYTEST_DONT_REWRITE."""

VERSION = "2.1.0"


def run_pytest():
    import pytest
    import sys

    class EditConfig:
        @pytest.hookimpl(hookwrapper=True)
        def pytest_cmdline_parse(pluginmanager, args):
            args.extend(
                [
                    "--tb=short",
                    "-o",
                    "console_output_style=classic",
                    "-o",
                    "default_alt_async_timeout=1",
                    "--log-level=INFO",
                    "-p",
                    "helpers_namespace",
                ]
            )
            yield

    sys.exit(pytest.main(plugins=[EditConfig()]))
