import re

from pyls import hookimpl

from noseOfYeti.tokeniser.spec_codec import codec

spec_codec = codec()

regexes = {
    "encoding": re.compile(r"#\s*coding\s*:\s*spec"),
    "first_whitespace": re.compile(r"^(\s*)"),
}


@hookimpl(hookwrapper=True)
def pyls_initialize(config, workspace):
    spec_codec.register(transform=True)
    yield


@hookimpl(hookwrapper=True)
def pyls_document_did_open(config, workspace, document):
    contents = document._source
    lines = contents.split("\n")

    if contents and regexes["encoding"].match(lines[0]):
        translated = spec_codec.translate(contents)
        translated = translated.split("\n")[: len(lines)]

        replacement = []
        for orig, new in zip(lines, translated):
            if new.startswith("class"):
                # We still need the root classes to be at the start of the document
                # So that their parent classes exist at that scope
                replacement.append(new)
            else:
                # Everything else however needs to be at their original indentation
                # So that pyls doesn't get confused by columns
                or_space = regexes["first_whitespace"].search(orig).groups()[0]
                tr_space = regexes["first_whitespace"].search(new).groups()[0]
                replacement.append(f"{or_space}{new[len(tr_space):]}")

        document._source = "\n".join(replacement)

    yield
