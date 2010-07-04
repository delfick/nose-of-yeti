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
    ###   MAKERS
    ########################

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
    
    def makeDescribe(self, value, nextDescribeKls):
        name = 'Test_%s' % self.acceptable(value)
        result = [ (NAME, name)
                 , (OP,   '(')
                 ]
        
        if nextDescribeKls:
            result.extend( self.tokensIn(nextDescribeKls) )
        else:
            result.extend( self.defaultKls )
        
        result.append( (OP, ')') )
    
        return result, name
        
    ########################
    ###   TRANSLATE
    ########################
    
    def translate(self, readline):
        result = [d for d in self.defaultImports]
        
        currentDescribeLevel = 0
        
        nextDescribeKls = None
        describeStack   = []
        indentAmounts   = []
        keepLastToken   = False
        startingAnIt    = False
        
        lookAtSpace = False
        afterSpace  = True
        justAppend  = False
        indentType  = ' '
        lastToken   = ' '
        
        # Looking at all the tokens
        for tokenum, value, (_, scol), (_, ecol), _ in generate_tokens(readline):
            # By default, we don't just append the value
            justAppend = False
            
            # Determine if working with spaces or tabs
            if tokenum == INDENT:
                indentType = value[0]
            
            # Ensuring NEWLINE tokens are actually specified as such
            if tokenum != NEWLINE and value == '\n':
                tokenum = NEWLINE
            
            # Determine next level of indentation
            if afterSpace and tokenum not in (NEWLINE, DEDENT, INDENT):
                if not indentAmounts or scol > indentAmounts[-1]:
                    indentAmounts.append( scol )
            
            # I want to change dedents into indents, because they seem to screw nesting up
            if tokenum == DEDENT:
                # Dedent means go back to last indentation
                if indentAmounts:
                    indentAmounts.pop()
                
                # Change the token
                tokenum = INDENT
                
                # Get last indent amount
                lastIndent = 0
                if indentAmounts:
                    lastIndent = indentAmounts[-1]
                
                # Make sure we don't have multiple indents in a row
                if result[-1][0] == INDENT:
                    result.pop()
                
                value = indentType * lastIndent
            
            # Determining what to replace and with what ::
            
            if afterSpace and tokenum == NAME:
                if value == 'describe':
                    # Dedenting describes removes them from being inheritable
                    while describeStack and describeStack[-1][0] >= scol:
                        describeStack.pop()
                    
                    currentDescribeLevel = scol
                    nextDescribeKls = None
                    
                    # Making sure this line starts at the beginning
                    # By editing previous INDENT
                    if result and result[-1][0] == INDENT:
                        result[-1] = (INDENT, result[-1][1][currentDescribeLevel:])
                    
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
                    if describeStack:
                        if not nextDescribeKls:
                            nextDescribeKls = describeStack[-1][1]
                    
                    res, name = self.makeDescribe(value, nextDescribeKls)
                    describeStack.append([currentDescribeLevel, name])
                    
                    result.extend( res )
                    
                elif lastToken == 'ignore':
                    startingAnIt = True
                    result.extend( self.makeIgnore(value) )
                
                else:
                    justAppend = True
            
            elif tokenum == NAME and lastToken == 'describe':
                nextDescribeKls = value
                keepLastToken = True
            
            elif tokenum == NEWLINE and lastToken != ':' and startingAnIt:
                result.extend( self.testSkip )
                             
            else:
                if tokenum == NEWLINE and lastToken == ':' and startingAnIt:
                    startingAnIt = False
                
                justAppend = True
            
            # Just apending if token isn't replaced and should be kept
            if justAppend:
                v = value
                
                # First ensure, the indentation has been normalised (incase of nesting)
                if tokenum == INDENT and currentDescribeLevel > 0:
                    v = value[currentDescribeLevel:]
                
                result.append([tokenum, v])
            
            # Storing current token if allowed to
            if not keepLastToken:
                lastToken = value
            else:
                keepLastToken = False
                
            # Determining if this token is whitespace at the beginning of the line so next token knows
            if value == '\n':
                afterSpace = True
                lookAtSpace = True
                
            else:
                afterSpace = False
                if lookAtSpace and (value == '' or whitespace.match(value)):
                    afterSpace = True
                    
                    if tokenum != INDENT:
                        # Only want to count at the beginning of the line
                        # Isn't reset till we have a newline
                        lookAtSpace = False
        
        #Remove trailing indents and dedents
        while result and result[-2][0] in (DEDENT, INDENT, ERRORTOKEN, NEWLINE):
            result.pop(-2)
        
        #Gone through all the tokens, returning now
        return result
