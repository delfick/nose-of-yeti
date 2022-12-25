from pathlib import Path
import typing as tp
import socketserver
import http.server
import webbrowser
import threading
import platform
import inspect
import socket
import shutil
import shlex
import time
import sys
import os

here = Path(__file__).parent

if platform.system() == "Windows":
    import mslex

    shlex = mslex  # noqa

if sys.version_info < (3, 10):
    Dict = tp.Dict
    List = tp.List
else:
    Dict = dict
    List = list


class Command:
    __is_command__: bool

    def __call__(self, bin_dir: Path, args: List[str]) -> None:
        ...


def command(func: tp.Callable) -> tp.Callable:
    tp.cast(Command, func).__is_command__ = True
    return func


def run(*args: tp.Union[str, Path], _env: tp.Optional[Dict[str, str]] = None) -> None:
    cmd = " ".join(shlex.quote(str(part)) for part in args)
    print(f"Running '{cmd}'")
    ret = os.system(cmd)
    if ret != 0:
        sys.exit(1)


class App:
    commands: Dict[str, Command]

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

    def __call__(self, args: List[str]) -> None:
        bin_dir = Path(sys.executable).parent

        if args and args[0] in self.commands:
            os.chdir(here.parent)
            self.commands[args[0]](bin_dir, args[1:])
            return

        sys.exit(f"Unknown command:\nAvailable: {sorted(self.commands)}\nWanted: {args}")

    @command
    def format(self, bin_dir: Path, args: List[str]) -> None:
        if not args:
            args = [".", *args]
        run(bin_dir / "black", *args)

    @command
    def lint(self, bin_dir: Path, args: List[str]) -> None:
        run(bin_dir / "pylama", *args)

    @command
    def tests(self, bin_dir: Path, args: List[str]) -> None:
        if "-q" not in args:
            args = ["-q", *args]
        run(bin_dir / "pytest", *args, _env={"NOSE_OF_YETI_BLACK_COMPAT": "false"})

    @command
    def tox(self, bin_dir: Path, args: List[str]) -> None:
        run(bin_dir / "tox", *args)

    @command
    def docs(self, bin_dir: Path, args: List[str]) -> None:
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
        run(bin_dir / "sphinx-build", "-b", "html", ".", "_build/html", "-d", "_build/doctrees")

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
