from noseOfYeti.tokeniser.spec_codec import codec

from pylama.config import LOGGER
from pylama.errors import Error
from pylama.main import shell

from unittest import mock
import codecs
import re


try:
    from pylama.core import CodeContext
except ImportError:
    CodeContext = None

spec_codec = codec()

regexes = {
    "position": re.compile(r"line (\d+), column (\d+)"),
    "encoding": re.compile(r"#\s*coding\s*:\s*spec"),
}


def translate(path: str, contents: str) -> str:
    lines = contents.split("\n")
    pattern = "%(filename)s:%(lnum)s:%(col)s: [%(type)s] %(text)s"

    if contents and regexes["encoding"].match(lines[0]):
        contents = spec_codec.translate(contents)

        if "--- internal spec codec error ---" in lines[-1]:
            found = []

            useful = False
            for line in lines[1:-2]:
                if useful or "SyntaxError:" in line:
                    found.append(line)
                    useful = True

            line = 0
            column = 1
            for line in found:
                m = regexes["position"].search(line)
                if m:
                    line, column = m.groups()
                    break

            msg = "\t".join(found)
            err = Error(linter="pylama", col=column, lnum=line, text=msg, filename=path)
            LOGGER.warning(pattern, err._info)

    return contents


def run_old_pylama(spec_codec):
    original = CodeContext.__enter__

    def interpret(self):
        ret = original(self)
        if not self.code:
            return ret

        self.code = translate(self.path, self.code)
        return ret

    with mock.patch.object(CodeContext, "__enter__", interpret):
        shell()


def run_pylama():
    spec_codec.register()

    if CodeContext is None:

        def better_read(filename: str) -> str:
            with codecs.open(filename) as fle:
                return translate(filename, fle.read())

        with mock.patch("pylama.context.read", better_read):
            return shell()
    else:
        run_old_pylama(spec_codec)
