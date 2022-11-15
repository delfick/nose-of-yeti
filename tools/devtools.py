from pathlib import Path
import typing as tp
import socketserver
import http.server
import webbrowser
import threading
import inspect
import socket
import shutil
import time
import sys
import sh
import os

here = Path(__file__).parent


class Command:
    __is_command__: bool

    def __call__(self, bin_dir: Path, args: tp.List[str]) -> None:
        ...


def command(func: tp.Callable) -> tp.Callable:
    tp.cast(Command, func).__is_command__ = True
    return func


class App:
    commands: tp.Dict[str, Command]

    def __init__(self):
        self.commands = {}

        compare = inspect.signature(type("C", (Command,), {})().__call__)

        for name in dir(self):
            val = getattr(self, name)
            if getattr(val, "__is_command__", False):
                assert (
                    inspect.signature(val) == compare
                ), f"Expected '{name}' to have correct signature, have {inspect.signature(val)} instead of {compare}"
                self.commands[name] = val

    def __call__(self, args: tp.List[str], *, venv_location: tp.Union[None, Path] = None) -> None:
        if venv_location is None:
            venv_location = Path(sys.executable) / ".." / ".."

        if args and args[0] in self.commands:
            os.chdir(here.parent)
            try:
                self.commands[args[0]](venv_location / "bin", args[1:])
            except sh.ErrorReturnCode as error:
                sys.exit(error.exit_code)
            return

        sys.exit(f"Unknown command:\nAvailable: {sorted(self.commands)}\nWanted: {args}")

    @command
    def format(self, bin_dir: Path, args: tp.List[str]) -> None:
        if not args:
            args = [".", *args]
        sh.Command(bin_dir / "black")(*args, _fg=True)

    @command
    def lint(self, bin_dir: Path, args: tp.List[str]) -> None:
        sh.Command(bin_dir / "pylama")(*args, _fg=True)

    @command
    def tests(self, bin_dir: Path, args: tp.List[str]) -> None:
        if "-q" not in args:
            args = ["-q", *args]
        sh.Command(bin_dir / "pytest")(*args, _fg=True)

    @command
    def tox(self, bin_dir: Path, args: tp.List[str]) -> None:
        sh.Command(bin_dir / "tox")(*args, _fg=True)

    @command
    def docs(self, bin_dir: Path, args: tp.List[str]) -> None:
        do_view: bool = False
        docs_path = here / ".." / "docs"
        for arg in args:
            if arg == "fresh":
                build_path = docs_path / "_build"
                if build_path.exists():
                    shutil.rmtree(build_path)
            elif arg == "view":
                do_view = True

        os.chdir(docs_path)
        sh.Command(bin_dir / "sphinx-build")(
            "-b", "html", ".", "_build/html", "-d", "_build/doctrees", _fg=True
        )

        if do_view:

            with socket.socket() as s:
                s.bind(("", 0))
                port = s.getsockname()[1]

            address = f"http://127.0.0.1:{port}"
            results = docs_path / "_build" / "html"

            class Handler(http.server.SimpleHTTPRequestHandler):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, directory=str(results), **kwargs)

            def open_browser():
                time.sleep(0.2)
                webbrowser.open(address)

            with socketserver.TCPServer(("", port), Handler) as httpd:
                print(f"Serving docs at {address}")
                thread = threading.Thread(target=open_browser)
                thread.daemon = True
                thread.start()
                try:
                    httpd.serve_forever()
                except KeyboardInterrupt:
                    pass


app = App()

if __name__ == "__main__":
    app(sys.argv[1:])
