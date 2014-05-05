from tokenize import untokenize
from encodings import utf_8
from six import StringIO
import encodings
import codecs
import six
import re

from noseOfYeti.tokeniser.imports import determine_imports
from noseOfYeti.tokeniser.tokeniser import Tokeniser
from noseOfYeti.tokeniser.config import Config

regexes = {
      'whitespace' : re.compile('\s*')
    , 'only_whitespace' : re.compile('^\s*$')
    , 'encoding_matcher' : re.compile("#\s*coding\s*:\s*spec")
    , 'leading_whitespace' : re.compile('^(\s*)[^\s]')
    }

class TokeniserCodec(object):
    """Class to register the spec codec"""
    def __init__(self, tokeniser):
        self.tokeniser = tokeniser

    def register(self):
        """Register spec codec"""
        # Assume utf8 encoding
        utf8 = encodings.search_function('utf8')

        class StreamReader(utf_8.StreamReader):
            """Used by cPython to deal with a spec file"""
            def __init__(sr, stream, *args, **kwargs):
                codecs.StreamReader.__init__(sr, stream, *args, **kwargs)
                data = self.dealwith(sr.stream.readline)
                sr.stream = StringIO(data)

        def decode(text, *args, **kwargs):
            """Used by pypy and pylint to deal with a spec file"""
            return_tuple = kwargs.get("return_tuple", True)

            if six.PY3:
                if hasattr(text, 'tobytes'):
                    text = text.tobytes().decode('utf8')
                else:
                    text = text.decode('utf8')

            buffered = StringIO(text)

            # Determine if we need to have imports for this string
            # It may be a fragment of the file
            has_spec = regexes['encoding_matcher'].search(buffered.readline())
            no_imports = not has_spec
            buffered.seek(0)

            # Translate the text
            if six.PY2:
                utf8 = encodings.search_function('utf8') # Assume utf8 encoding
                reader = utf8.streamreader(buffered)
            else:
                reader = buffered

            data = self.dealwith(reader.readline, no_imports=no_imports)

            # If nothing was changed, then we want to use the original file/line
            # Also have to replace indentation of original line with indentation of new line
            # To take into account nested describes
            if text and not regexes['only_whitespace'].match(text):
                if regexes['whitespace'].sub('', text) == regexes['whitespace'].sub('', data):
                    bad_indentation = regexes['leading_whitespace'].search(text).groups()[0]
                    good_indentation = regexes['leading_whitespace'].search(data).groups()[0]
                    data = '%s%s' % (good_indentation, text[len(bad_indentation):])

            # If text is empty and data isn't, then we should return text
            if len(text) == 0 and len(data) == 1:
                if return_tuple:
                    return "", 0
                else:
                    return ""

            # Return translated version and it's length
            if return_tuple:
                return data, len(data)
            else:
                return data

        incrementaldecoder = utf8.incrementaldecoder
        if six.PY3:
            def incremental_decode(decoder, *args, **kwargs):
                """Wrapper for decode from IncrementalDecoder"""
                kwargs["return_tuple"] = False
                return decode(*args, **kwargs)
            incrementaldecoder = type("IncrementalDecoder", (utf8.incrementaldecoder, ), {"decode": incremental_decode})

        def search_function(s):
            """Determine if a file is of spec encoding and return special CodecInfo if it is"""
            if s != 'spec': return None
            return codecs.CodecInfo(
                  name='spec'
                , encode=utf8.encode
                , decode=decode
                , streamreader=StreamReader
                , streamwriter=utf8.streamwriter
                , incrementalencoder=utf8.incrementalencoder
                , incrementaldecoder=incrementaldecoder
                )

        # Do the register
        codecs.register(search_function)

    def dealwith(self, readline, **kwargs):
        """
            Replace the contents of spec file with the translated version
            readline should be a callable object
            , which provides the same interface as the readline() method of built-in file objects
        """
        data = []
        try:
            # We pass in the data variable as an argument so that we
            # get partial output even in the case of an exception.
            self.tokeniser.translate(readline, data, **kwargs)
        except Exception as e:
            # Comment out partial output so that it doesn't result in
            # a syntax error when received by the interpreter.
            lines = []
            for line in untokenize(data).split('\n'):
                lines.append("# {0}".format(line))

            # Create exception to put into code to announce error
            exception = 'raise Exception("""--- internal spec codec error --- {0}""")'.format(e)

            # Need to make sure the exception doesn't add a new line and put out line numberes
            if len(lines) == 1:
                data = "{0}{1}".format(exception, lines[0])
            else:
                lines.append(exception)
                first_line = lines.pop()
                lines[0] = "{0} {1}".format(first_line, lines[0])
                data = '\n'.join(lines)
        else:
            # At this point, data is a list of tokens
            data = untokenize(data)

        if six.PY2 and type(data) is not unicode:
            data = unicode(data)

        return data

    def output_for_debugging(self, stream, data):
        """It will write the translated version of the file"""
        with open('%s.spec.out' % stream.name, 'w') as f: f.write(str(data))

########################
###   CODEC REGISTER
########################

def register_from_options(options=None, template=None, extractor=None):
    """Register the spec codec using the provided options"""
    if template is None:
        from noseOfYeti.plugins.support.spec_options import spec_options as template

    if extractor is None:
        from noseOfYeti.plugins.support.spec_options import extract_options_dict as extractor

    config = Config(template)
    config.setup(options, extractor)

    imports = determine_imports(
          extra_imports = ';'.join([d for d in config.extra_import if d])
        , with_default_imports = config.with_default_imports
        )

    tok = Tokeniser(
          default_kls = config.default_kls
        , import_tokens = imports
        , wrapped_setup = config.wrapped_setup
        , with_describe_attrs = not config.no_describe_attrs
        )

    TokeniserCodec(tok).register()

