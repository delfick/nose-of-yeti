from noseOfYeti.tokeniser.spec_codec import codec

from pylama.core import CodeContext
from pylama.config import LOGGER
from pylama.errors import Error
from pylama.main import shell
from unittest import mock
import re

regexes = {
    "position": re.compile(r"line (\d+), column (\d+)"),
    "encoding": re.compile(r"#\s*coding\s*:\s*spec"),
}


def run_pylama():
    spec_codec = codec()
    spec_codec.register()

    original = CodeContext.__enter__
    pattern = "%(filename)s:%(lnum)s:%(col)s: [%(type)s] %(text)s"

    def interpret(self):
        ret = original(self)
        if not self.code:
            return ret

        contents = self.code
        lines = self.code.split("\n")

        if contents and regexes["encoding"].match(lines[0]):
            self.code = spec_codec.translate(contents)

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
                err = Error(linter="pylama", col=column, lnum=line, text=msg, filename=self.path)
                LOGGER.warning(pattern, err._info)

        return ret

    with mock.patch.object(CodeContext, "__enter__", interpret):
        shell()
