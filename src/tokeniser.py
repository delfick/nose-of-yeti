from encodings import utf_8
from tokenize import *
import cStringIO
import encodings
import codecs
import re

whitespace = re.compile('\s+')

def translate(readline):
    result = [ (NAME, 'import')
             , (NAME, 'nose')
             , (OP,   ';')
             , (NAME, 'from')
             , (NAME, 'nose.tools')
             , (NAME, 'import')
             , (OP,   '*')
             , (OP, ';')
             , (NAME, 'from')
             , (NAME, 'should_dsl')
             , (NAME, 'import')
             , (OP,   '*')
             , (NEWLINE, '\n')
             ]
    
    indentLevel = 0
    startingAnIt  = False
    lastToken   = ' '
    afterSpace  = True
    
    for tokenum, value, _, _, _ in generate_tokens(readline):
        
        if lastToken == '\n':
            afterSpace = True
        else:
            if afterSpace and lastToken not in ('\n', ''):
                if whitespace.match(lastToken):
                    afterSpace = True
                else:
                    afterSpace = False
        
        if afterSpace and tokenum == NAME and value == 'describe':
            result.append(
                          [tokenum, 'class']
                         )
            
        elif afterSpace and tokenum == NAME and value == 'it':
            result.append(
                          [tokenum, 'def']
                         )
            
        elif afterSpace and tokenum == NAME and value == 'before_each':
            result.extend(
                          [ (NAME, 'def')
                          , (NAME, 'setUp')
                          , (OP,   '(')
                          , (NAME, 'self')
                          , (OP,   ')')
                          ]
                         )
                           
        elif afterSpace and tokenum == NAME and value == 'after_each':
            result.extend(
                          [ (NAME, 'def')
                          , (NAME, 'tearDown')
                          , (OP,   '(')
                          , (NAME, 'self')
                          , (OP,   ')')
                          ]
                         )
                           
        elif tokenum == STRING and lastToken == 'it':
            startingAnIt = True
            result.extend(
                          [ [NAME, 'test_%s' % value.replace(' ', '_').replace("'", '').replace('"', '')]
                          , [OP,   '(']
                          , [NAME, 'self']
                          , [OP,   ')']
                          ]
                         )
                           
        elif tokenum == STRING and lastToken == 'describe':
            result.extend(
                          [ [NAME, 'test_%s' % value.replace(' ', '_').replace("'", '').replace('"', '')]
                          , [OP,   '(']
                          , [NAME, 'object']
                          , [OP,   ')']
                          ]
                         )
        
        elif tokenum == NEWLINE and lastToken != ':' and startingAnIt:
            result.extend(
                          [ (OP,   ':')
                          , (NAME, 'raise')
                          , (NAME, 'nose.SkipTest')
                          , (NEWLINE, '\n')
                          ]
                         )
                         
        else:
            if tokenum == NEWLINE and lastToken == ':' and startingAnIt:
                startingAnIt = False
                
            result.append([tokenum, value])
        
        lastToken = value
        
    return result


class StreamReader(utf_8.StreamReader):
    def __init__(self, *args, **kwargs):
        codecs.StreamReader.__init__(self, *args, **kwargs)
        data = untokenize(translate(self.stream.readline))
        self.stream = cStringIO.StringIO(data)

def searchFunction(s):
    if s != 'spec': return None
    utf8 = encodings.search_function('utf8') # Assume utf8 encoding
    return codecs.CodecInfo(
          name   = 'spec'
        , encode = utf8.encode
        , decode = utf8.decode
        , streamreader = StreamReader
        , streamwriter = utf8.streamwriter
        , incrementalencoder = utf8.incrementalencoder
        , incrementaldecoder = utf8.incrementaldecoder
        )

codecs.register(searchFunction)
