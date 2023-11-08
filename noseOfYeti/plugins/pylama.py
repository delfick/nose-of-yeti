import codecs
import re

import pylama.context
from pylama.config import LOGGER
from pylama.errors import Error
from pylama.lint import Linter as BaseLinter

from noseOfYeti.tokeniser.spec_codec import codec, register

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

            lnum = "0"
            column = "1"
            for line in found:
                m = regexes["position"].search(line)
                if m:
                    lnum, column = m.groups()
                    break

            msg = "\t".join(found)
            err = Error(linter="pylama", col=int(column), lnum=int(lnum), text=msg, filename=path)
            LOGGER.warning(pattern, err._info)

    return contents


def better_read(filename: str) -> str:
    with codecs.open(filename) as fle:
        return translate(filename, fle.read())


def setup():
    register(transform=True)
    pylama.context.read = better_read


class Linter(BaseLinter):
    def allow(self, path):
        return False

    def run(self, path, **meta):
        return []


setup()
