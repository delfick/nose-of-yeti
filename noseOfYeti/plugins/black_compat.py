import os
import re
import sys
import tempfile
from pathlib import Path

load_grammar_line = '_GRAMMAR_FILE = os.path.join(os.path.dirname(__file__), "Grammar.txt")'


def is_supported_black_version():
    # I'm caring too much about internals to be confident
    # about future compatibility
    try:
        import black  # noqa
        import blib2to3  # noqa
        import importlib_resources  # noqa
    except ImportError:
        return

    return not black.COMPILED and black.__version__ == "22.10.0"


def maybe_modify_black():
    if os.environ.get("NOSE_OF_YETI_BLACK_COMPAT") == "true":
        modify_black()


def replace_pygram():
    from importlib.machinery import ModuleSpec, SourceFileLoader
    from importlib.util import module_from_spec

    import importlib_resources as resources

    for k, m in list(sys.modules.items()):
        if "blib2to3" in k or "black" in k:
            del sys.modules[k]

    with resources.as_file(
        resources.files("noseOfYeti").joinpath("black", "Grammar.noy.txt")
    ) as noy_grammar_path:
        if noy_grammar_path.exists():
            location = Path(__import__("blib2to3").__file__).parent / "Grammar.noy.txt"
            current = None
            if location.exists():
                with open(location) as crnt:
                    current = crnt.read()

            with open(noy_grammar_path) as ngp:
                content = ngp.read()
                if content != current:
                    with open(location, "w") as fle:
                        fle.write(content)

        with tempfile.TemporaryDirectory() as directory:
            location = Path(directory) / "pygram.py"
            with open(location, "w") as fle:
                noy_grammar_line = (
                    '_GRAMMAR_FILE = os.path.join(os.path.dirname(__file__), "Grammar.noy.txt")'
                )
                fle.write(
                    (resources.files("blib2to3") / "pygram.py")
                    .read_text()
                    .replace(load_grammar_line, noy_grammar_line)
                )

            loader = SourceFileLoader("pygram", location)
            mod = module_from_spec(ModuleSpec("pygram", loader))
            mod.__file__ = str(resources.files("blib2to3").joinpath("pygram.py"))
            mod.__package__ = "blib2to3"
            loader.exec_module(mod)
            sys.modules["blib2to3.pygram"] = mod


def modify_black(spec_codec=None):
    """
    This will make it so calling black after this in the same session will
    deal with noseOfYeti spec files.
    """
    if not is_supported_black_version():
        return

    import blib2to3
    from blib2to3 import pygram

    if not str(pygram.__loader__.path).startswith(str(Path(blib2to3.__file__).parent)):
        return
    del pygram
    del blib2to3

    if spec_codec is None:
        from noseOfYeti.tokeniser.spec_codec import codec, register

        spec_codec = codec()
        register(transform=False)

    replace_pygram()

    import black
    from black.linegen import LineGenerator
    from blib2to3.pgen2 import parse as blibparse

    token = blibparse.token
    Parser = blibparse.Parser

    class ModifiedLineGenerator(LineGenerator):
        def visit_setup_teardown_stmts(self, node):
            yield from self.line()
            yield from self.visit_default(node)

        def visit_describe_stmt(self, node):
            yield from self.line()
            yield from self.visit_default(node)

        def visit_it_stmt(self, node):
            yield from self.line()
            yield from self.visit_default(node)

    class ModifiedParser(Parser):
        def classify(self, type, value, context):
            special = [
                "it",
                "ignore",
                "context",
                "describe",
                "before_each",
                "after_each",
            ]
            if type == token.NAME and value in special:
                dfa, state, node = self.stack[-1]
                if node and node[-1]:
                    if node[-1][-1].type < 256 and node[-1][-1].type not in (
                        token.INDENT,
                        token.DEDENT,
                        token.NEWLINE,
                        token.ASYNC,
                    ):
                        return [self.grammar.tokens.get(token.NAME)]
            return super().classify(type, value, context)

    original_assert_equivalent = black.assert_equivalent

    def assert_equivalent(src, dst):
        if src and re.match(r"#\s*coding\s*:\s*spec", src.split("\n")[0]):
            src = spec_codec.translate(src, transform=True)
            dst = spec_codec.translate(dst, transform=True)
        original_assert_equivalent(src, dst)

    blibparse.Parser = ModifiedParser
    black.LineGenerator = ModifiedLineGenerator
    black.assert_equivalent = assert_equivalent
