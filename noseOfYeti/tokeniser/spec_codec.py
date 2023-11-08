import codecs
import encodings
import re
import sys
import traceback
from encodings import utf_8
from io import StringIO
from tokenize import untokenize

from noseOfYeti.tokeniser.tokeniser import Tokeniser

regexes = {
    "whitespace": re.compile(r"\s*"),
    "only_whitespace": re.compile(r"^\s*$"),
    "encoding_matcher": re.compile(r"#\s*coding\s*:\s*spec"),
    "leading_whitespace": re.compile(r"^(\s*)[^\s]"),
}


class TokeniserCodec:
    """Class to register the spec codec"""

    def __init__(self, tokeniser):
        self.tokeniser = tokeniser

        self.transform = True
        self.codec = self.get_codec()

    def translate(self, value, transform=None):
        if isinstance(value, str):
            value = value.encode()

        return self.codec.decode(
            value, return_tuple=False, transform=self.transform if transform is None else transform
        )

    def register(self):
        def search_function(s):
            """Determine if a file is of spec encoding and return special CodecInfo if it is"""
            if s != "spec":
                return None
            return self.codec

        # Do the register
        codecs.register(search_function)

    def get_codec(self):
        """Register spec codec"""
        # Assume utf8 encoding
        utf8 = encodings.search_function("utf8")

        class StreamReader(utf_8.StreamReader):
            """Used by cPython to deal with a spec file"""

            def __init__(sr, stream, *args, **kwargs):
                codecs.StreamReader.__init__(sr, stream, *args, **kwargs)
                if self.transform:
                    data = self.dealwith(sr.stream.readline)
                    sr.stream = StringIO(data)

        def _decode(text, *args, transform=None, **kwargs):
            transform = self.transform if transform is None else transform

            if not transform:
                return utf8.decode(text, *args, **kwargs)

            if hasattr(text, "tobytes"):
                text = text.tobytes().decode()
            else:
                text = text.decode()

            reader = StringIO(text)

            # Determine if we need to have imports for this string
            # It may be a fragment of the file
            has_spec = regexes["encoding_matcher"].search(reader.readline())
            no_imports = not has_spec
            reader.seek(0)

            data = self.dealwith(reader.readline, no_imports=no_imports)

            # If nothing was changed, then we want to use the original file/line
            # Also have to replace indentation of original line with indentation of new line
            # To take into account nested describes
            if text and not regexes["only_whitespace"].match(text):
                if regexes["whitespace"].sub("", text) == regexes["whitespace"].sub("", data):
                    bad_indentation = regexes["leading_whitespace"].search(text).groups()[0]
                    good_indentation = regexes["leading_whitespace"].search(data).groups()[0]
                    data = f"{good_indentation}{text[len(bad_indentation) :]}"

            # If text is empty and data isn't, then we should return text
            if len(text) == 0 and len(data) == 1:
                return "", 0

            # Return translated version and it's length
            return data, len(data)

        def decode(text, *args, return_tuple=True, transform=None, **kwargs):
            ret = _decode(text, *args, transform=transform, **kwargs)
            if return_tuple:
                return ret
            else:
                return ret[0]

        class incrementaldecoder(utf8.incrementaldecoder):
            def decode(s, obj, final, **kwargs):
                if not self.transform:
                    return super().decode(obj, final, **kwargs)

                lines = obj.split("\n".encode("utf-8"))
                if re.match(r"#\s*coding:\s*spec", lines[0].decode("utf-8", "replace")) and final:
                    kwargs["return_tuple"] = False
                    return decode(obj, final, **kwargs)
                else:
                    return super().decode(obj, final, **kwargs)

        return codecs.CodecInfo(
            name="spec",
            encode=utf8.encode,
            decode=decode,
            streamreader=StreamReader,
            streamwriter=utf8.streamwriter,
            incrementalencoder=utf8.incrementalencoder,
            incrementaldecoder=incrementaldecoder,
        )

    def dealwith(self, readline, **kwargs):
        """
        Replace the contents of spec file with the translated version
        readline should be a callable object,
        which provides the same interface as the readline() method of built-in file objects
        """
        data = []
        try:
            # We pass in the data variable as an argument so that we
            # get partial output even in the case of an exception.
            self.tokeniser.translate(readline, data, **kwargs)
        except:
            lines = ['msg = r"""']
            for line in traceback.format_exception(*sys.exc_info()):
                lines.append(line.strip())
            lines.append('"""')
            lines.append(r'raise Exception(f"--- internal spec codec error --- \n{msg}")')
            data = "\n".join(lines)
        else:
            # At this point, data is a list of tokens
            data = untokenize(data)

        # python3.9 requires a newline at the end
        data += "\n"

        return data

    def output_for_debugging(self, stream, data):
        """It will write the translated version of the file"""
        with open(f"{stream.name}.spec.out", "w") as f:
            f.write(str(data))


########################
###   CODEC REGISTER
########################

_spec_codec = None


def codec():
    """Return the codec used to translate a file"""
    global _spec_codec
    if _spec_codec is None:
        _spec_codec = TokeniserCodec(Tokeniser())
    return _spec_codec


def register(transform=True):
    """Get a codec and register it in python"""
    do_register = False
    try:
        codecs.lookup("spec")
    except LookupError:
        do_register = True

    cdc = codec()
    cdc.transform = transform

    if do_register:
        cdc.register()
