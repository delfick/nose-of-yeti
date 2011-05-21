from encodings import utf_8
from string import capwords
from tokenize import *
import cStringIO
import encodings
import codecs
import re

whitespace = re.compile('\s+')

regexes = {
      'joins': re.compile('[ -]')
    , 'whitespace': re.compile('\s+')
    , 'punctuation': re.compile('[\'",.;?{()}#]')
    }
        
class Tokeniser(object): 

    def __init__(self, defaultKls='object', extraImports=None, withDefaultImports=True, withDescribeAttrs=True):
        self.withDefaultImports = withDefaultImports
        self.withDescribeAttrs = withDescribeAttrs
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
        return regexes['punctuation'].sub("", regexes['joins'].sub("_", value))
        
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
    
    def getEquivalence(self, name):
        return { 'before_each' : 'setUp'
               , 'after_each'  : 'tearDown'
               }.get(name, name)
            
    ########################
    ###   MAKERS
    ########################

    def constructReplacements(self):
        self.before_each = [
              (NAME, 'def')
            , (NAME, self.getEquivalence('before_each'))
            , (OP,   '(')
            , (NAME, 'self')
            , (OP,   ')')
            ]
        
        self.after_each =  [
              (NAME, 'def')
            , (NAME, self.getEquivalence('after_each'))
            , (OP,   '(')
            , (NAME, 'self')
            , (OP,   ')')
            ]
        
        self.testSkip = [
              (OP,   ':')
            , (NAME, 'raise')
            , (NAME, 'nose.SkipTest')
            ]
        
        self.endIt = [ (OP,   ')')]
    
    def startIt(self, value):
        return  [ (NAME, 'test_%s' % self.acceptable(value))
                , (OP,   '(')
                , (NAME, 'self')
                ]
                
    def startIgnore(self, value):
        return  [ (NAME, 'ignore__%s' % self.acceptable(value))
                , (OP,   '(')
                , (NAME, 'self')
                ]
    
    def makeDescribe(self, value, nextDescribeKls, inheriting=False):
        name = capwords(self.acceptable(value), '_')
        if nextDescribeKls and inheriting:
            use = nextDescribeKls
            if use.startswith('Test'):
                use = use[4:]
            name = 'Test{0}_{1}'.format(use, name)
        else:
            name = 'Test{0}'.format(name)

        result = [ (NAME, name)
                 , (OP,   '(')
                 ]
        if nextDescribeKls:
            result.extend( self.tokensIn(nextDescribeKls) )
        else:
            result.extend( self.defaultKls )
        result.append( (OP, ')') )
        return result, name
    
    def makeSuper(self, nextDescribeKls):
        if nextDescribeKls:
            kls = self.tokensIn(nextDescribeKls)
        else:
            kls = self.defaultKls
            
        result = [ (NAME, 'sup')
                 , (OP,   '=')
                 , (NAME, 'super')
                 , (OP,   '(')
                 ]
        
        result.extend(kls)
            
        result.extend(
            [ (OP,   ',')
            , (NAME, 'self')
            , (OP,   ')')
            , (NEWLINE, '\n')
            ]
        )
        
        return result
        
    def useSuper(self, method):
        method = self.getEquivalence(method)
        
        return [ (NAME,   'if')
               , (NAME,   'hasattr')
               , (OP,     '(')
               , (OP,     'sup')
               , (OP,     ',')
               , (OP,     '"')
               , (STRING, method)
               , (OP,     '"')
               , (OP,     ')')
               , (OP,     ':')
               , (NAME,   'sup')
               , (OP,     '.')
               , (NAME,   method)
               , (OP,     '(')
               , (OP,     ')')
               , (NEWLINE, '\n')
               ]
    
    def makeDescribeAttr(self, describe):
        return [ (NEWLINE, '\n')
               , (NAME, describe)
               , (OP,   '.')
               , (NAME, 'is_noy_spec')
               , (OP,   '=')
               , (NAME, 'True')
               ]
               
    ########################
    ###   TRANSLATE
    ########################
    
    def translate(self, readline):
        result = [d for d in self.defaultImports]
        
        currentDescribeLevel = 0
        
        nextDescribeKls = None
        adjustIndentAt  = []
        describeStack   = []
        indentAmounts   = []
        keepLastToken   = False
        startingAnIt    = False
        allDescribes    = []
        
        skippedTest = True
        lookAtSpace = False
        inheriting  = False
        afterSpace  = True
        justAppend  = False
        indentType  = ' '
        ignoreNext  = None
        groupStack  = []
        lastToken   = ' '
        endedIt     = False
        emptyDescr  = False
        
        # Looking at all the tokens
        for tokenum, value, (_, scol), (_, ecol), _ in generate_tokens(readline):
            # Sometimes we need to ignore stuff
            if ignoreNext:
                nextIgnore = ignoreNext
                if type(ignoreNext) is list:
                    nextIgnore = ignoreNext.pop(0)
                
                if nextIgnore == (tokenum, value):
                    continue
                else:
                    nextIgnore = None
            
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
                if not groupStack:
                    # We don't care about indentation inside a group (list, tuple or dictionary)
                    if not indentAmounts or scol > indentAmounts[-1]:
                        indentAmounts.append( scol )
                    
                    while adjustIndentAt:
                        result[adjustIndentAt.pop()] = (INDENT, indentType * (scol - currentDescribeLevel))
            
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
            
            #Determine if we have an it to close
            if startingAnIt and not endedIt and (value == ":" or tokenum == NEWLINE):
                result.extend( self.endIt )
                endedIt = True
                
            # Determining what to replace and with what ::
            if tokenum == OP:
                if value in ['(', '[', '{']:
                    # add to the stack because we started a list
                    groupStack.append(value)
                    emptyDescr = False

                elif value in [')', ']', '}']:
                    # not necessary to check for correctness
                    groupStack.pop()
                    
                justAppend = True
                
            elif afterSpace and tokenum == NAME:
                if value in ('describe', 'context'):
                    # Make sure we dedent if we just made a skip test
                    if skippedTest:
                        result.append( (INDENT, indentType * (scol - currentDescribeLevel)) )
                        skippedTest = False
                        
                    # Make sure we insert a pass if we inserted an empty describe.
                    if emptyDescr and scol > currentDescribeLevel:
                        while result[-1][0] in (INDENT, NEWLINE):
                            result.pop()
                        result.append( (NAME, 'pass') )
                        result.append( (NEWLINE, '\n') )
                        result.append( (INDENT, indentType * scol) )
                        
                    emptyDescr = True

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
                    skippedTest = False
                    emptyDescr = False
                    result.append( (NAME, 'def') )
                    
                elif value in ('before_each', 'after_each'):
                    skippedTest = False
                    emptyDescr = False
                    result.extend( getattr(self, value) )
                    if describeStack:
                        expecting = [ (OP,      ':')
                                    , (NEWLINE, '\n')
                                    ]
                        
                        result.extend(expecting)
                        ignoreNext = expecting
                        
                        adjustIndentAt.append(len(result))
                        result.append( (INDENT, '') )
                        result.extend( self.makeSuper(describeStack[-1][1]) )
                        
                        adjustIndentAt.append(len(result))
                        result.append( (INDENT, '') )
                        result.extend( self.useSuper(value) )
                    
                else:
                    skippedTest = False
                    emptyDescr = False
                    justAppend = True
                               
            elif tokenum == STRING:
                if lastToken == 'it':
                    endedIt = False
                    startingAnIt = True
                    result.extend( self.startIt(value) )
                               
                elif lastToken in ('describe', 'context'):
                    inheritance = False
                    if describeStack:
                        if not nextDescribeKls:
                            inheritance = True
                            nextDescribeKls = describeStack[-1][1]
                    
                    res, name = self.makeDescribe(value, nextDescribeKls, inheritance)
                    describeStack.append([currentDescribeLevel, name])
                    allDescribes.append(name)
                    
                    result.extend( res )
                    
                elif lastToken == 'ignore':
                    endedIt = False
                    startingAnIt = True
                    result.extend( self.startIgnore(value) )
                
                else:
                    emptyDescr = False
                    justAppend = True
            
            elif tokenum == NAME and lastToken in ('describe', 'context'):
                nextDescribeKls = value
                keepLastToken = True
            
            elif tokenum == NEWLINE and lastToken != ':' and startingAnIt:
                result.extend( self.testSkip )
                startingAnIt = False
                skippedTest = True
                justAppend = True
                             
            else:
                if tokenum == NEWLINE and lastToken == ':' and startingAnIt:
                    startingAnIt = False
                if tokenum not in (NEWLINE, INDENT):
                    emptyDescr = False
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
                if lookAtSpace and (value == '' or regexes['whitespace'].match(value)):
                    afterSpace = True
                    
                    if tokenum != INDENT:
                        # Only want to count at the beginning of the line
                        # Isn't reset till we have a newline
                        lookAtSpace = False
        
        if startingAnIt and not endedIt:
            result.extend(self.endIt)
            if lastToken != ':':
                result.extend(self.testSkip)
            
        # Remove trailing indents and dedents
        while result and result[-2][0] in (INDENT, ERRORTOKEN, NEWLINE):
            result.pop(-2)
        
        # Add attributes to our Describes so that the plugin can handle some nesting issues
        # Where we have tests in upper level describes being run in lower level describes
        if self.withDescribeAttrs and allDescribes:
            result.append( (NEWLINE, '\n') )
            result.append( (INDENT, '') )
            
            for describe in allDescribes:
                result.extend( self.makeDescribeAttr(describe) )
        
        #Gone through all the tokens, returning now
        return result
