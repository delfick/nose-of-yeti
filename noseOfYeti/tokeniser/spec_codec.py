from tokenize import untokenize
from encodings import utf_8
from string import capwords
import cStringIO
import encodings
import codecs
import re

class TokeniserCodec(object):
    """Class to register the spec codec"""
    def __init__(self, tokeniser):
        self.tokeniser = tokeniser
    
    def register(self):
        """Register spec codec"""
        class StreamReader(utf_8.StreamReader):
            """Used by cPython to deal with a spec file"""
            def __init__(sr, stream, *args, **kwargs):
                codecs.StreamReader.__init__(sr, stream, *args, **kwargs)
                data = self.dealwith(sr.stream.readline)
                sr.stream = cStringIO.StringIO(data)
        
        def decode(text, *args):
            """Used by pypy to deal with a spec file"""
            utf8 = encodings.search_function('utf8') # Assume utf8 encoding
            reader = utf8.streamreader(cStringIO.StringIO(text))
            data = self.dealwith(reader.readline)
            return unicode(data), len(data)
        
        def search_function(s):
            """Determine if a file is of spec encoding and return special CodecInfo if it is"""
            if s != 'spec': return None
            utf8 = encodings.search_function('utf8') # Assume utf8 encoding
            return codecs.CodecInfo(
                  name='spec'
                , encode=utf8.encode
                , decode=decode
                , streamreader=StreamReader
                , streamwriter=utf8.streamwriter
                , incrementalencoder=utf8.incrementalencoder
                , incrementaldecoder=utf8.incrementaldecoder
                )
            
        # Do the register
        codecs.register(search_function)
    
    def dealwith(self, readline):
        """
            Replace the contents of spec file with the translated version
            readline should be a callable object
            , which provides the same interface as the readline() method of built-in file objects
        """
        data = []
        try:
            # We pass in the data variable as an argument so that we
            # get partial output even in the case of an exception.
            self.tokeniser.translate(readline, data)
        except Exception as e:
            # Comment out partial output so that it doesn't result in
            # a syntax error when received by the interpreter.
            data = '\n'.join([
                  re.sub('^', '#', untokenize(data), 0, re.MULTILINE)
                , 'raise Exception("""--- internal spec codec error ---\n%s""")' % e
                ])
            # Join two lines at the beginning of the partial output so that
            # we get the exception in the right line and still can see
            # all code in the debug output.
            data = ''.join(data.split('\n', 2))
        else:
            # At this point, data is a list of tokens
            data = untokenize(data)
        
        return data
    
    def output_for_debugging(stream, data):
        """It will write the translated version of the file"""
        with open('%s.spec.out' % stream.name, 'w') as f: f.write(data)