from encodings import utf_8
from tokenize import *
import cStringIO
import encodings
import codecs
import re

whitespace = re.compile('\s+')
        
class Tokeniser(object): 

    def __init__(self, defaultKls='object', extraImports=None, withDefaultImports=True):
        self.withDefaultImports = withDefaultImports
        self.defaultImports = self.determineImports(extraImports)
        self.defaultKls = self.tokensIn(defaultKls)
        self.constructReplacements()
    
    ########################
    ###   REGISTER
    ########################
    
    def register(self):
    
        class StreamReader(utf_8.StreamReader):
            def __init__(sr, *args, **kwargs):
                codecs.StreamReader.__init__(sr, *args, **kwargs)
                data = untokenize(self.translate(sr.stream.readline))
                sr.stream = cStringIO.StringIO(data)

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
        
    ########################
    ###   UTILITY
    ########################
    
    def determineImports(self, extra):
        
        if extra:
            default = extra
        else:
            default = []
        
        if type(extra) in (str, unicode):
            default = self.tokensIn(extra)
        
        else:
            temp = []
            
            for d in default:
                if d[0] == NEWLINE:
                    # I want to make sure the extra imports don't 
                    # Take up extra lines in the code than the "# coding: spec"
                    temp.append( (OP, ';') )
                else:
                    temp.append(d)
        
        if default:
            if tuple(default[-1]) != (OP, ';'):
                default.append( (OP, ';') )
        
        if self.withDefaultImports:
            default.extend(
                self.tokensIn('import nose; from nose.tools import *; from should_dsl import *')
            )
        
        return default

    def constructReplacements(self):
        self.before_each = [
              (NAME, 'def')
            , (NAME, 'setUp')
            , (OP,   '(')
            , (NAME, 'self')
            , (OP,   ')')
            ]
        
        self.after_each =  [
              (NAME, 'def')
            , (NAME, 'tearDown')
            , (OP,   '(')
            , (NAME, 'self')
            , (OP,   ')')
            ]
        
        self.testSkip = [
              (OP,   ':')
            , (NAME, 'raise')
            , (NAME, 'nose.SkipTest')
            , (NEWLINE, '\n')
            ]
        
    
    def makeIt(self, value):
        return  [ (NAME, 'test_%s' % self.acceptable(value))
                , (OP,   '(')
                , (NAME, 'self')
                , (OP,   ')')
                ]
                
    def makeIgnore(self, value):
        return  [ (NAME, 'ignore__%s' % self.acceptable(value))
                , (OP,   '(')
                , (NAME, 'self')
                , (OP,   ')')
                ]
    
    def makeDescribe(self, value):
        result = [ (NAME, 'test_%s' % self.acceptable(value))
                 , (OP,   '(')
                 ]
        
        result.extend( self.defaultKls )
        
        result.append( (OP, ')') )
    
        return result
    
    def acceptable(self, value):
        return value.replace(' ', '_').replace("'", '').replace('"', '')
        
    def tokensIn(self, s):
        self.taken = False
        def get():
            #Making generate_tokens not loop forever
            if not self.taken:
                self.taken = True
                return s.strip()
            else:
                return ''
            
        return [(t, v) for t, v, _, _, _ in generate_tokens(get)][:-1]
        
    ########################
    ###   TRANSLATE
    ########################
    
    def translate(self, readline):
        result = [d for d in self.defaultImports]
        
        indentLevel = 0
        startingAnIt  = False
        afterSpace  = True
        justAppend  = False
        lastToken   = ' '
        
        for tokenum, value, _, _, _ in generate_tokens(readline):
            justAppend = False
            
            if lastToken == '\n':
                afterSpace = True
            else:
                if afterSpace and lastToken not in ('\n', ''):
                    if whitespace.match(lastToken):
                        afterSpace = True
                    else:
                        afterSpace = False
            
            if afterSpace and tokenum == NAME:
                if value == 'describe':
                    result.append( (NAME, 'class') )
                
                elif value in ('it', 'ignore'):
                    result.append( (NAME, 'def') )
                    
                elif value == 'before_each':
                    result.extend( self.before_each )
                                   
                elif value == 'after_each':
                    result.extend( self.after_each )
                    
                else:
                    justAppend = True
                               
            elif tokenum == STRING:
                if lastToken == 'it':
                    startingAnIt = True
                    result.extend( self.makeIt(value) )
                               
                elif lastToken == 'describe':
                    result.extend( self.makeDescribe(value) )
                    
                elif lastToken == 'ignore':
                    startingAnIt = True
                    result.extend( self.makeIgnore(value) )
                
                else:
                    justAppend = True
            
            elif tokenum == NEWLINE and lastToken != ':' and startingAnIt:
                result.extend( self.testSkip )
                             
            else:
                if tokenum == NEWLINE and lastToken == ':' and startingAnIt:
                    startingAnIt = False
                
                justAppend = True
            
            if justAppend:
                result.append([tokenum, value])
            
            lastToken = value
            
        return result
