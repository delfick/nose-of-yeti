from encodings import utf_8
from string import capwords
from tokenize import *
import cStringIO
import encodings
import codecs
import re

regexes = {
      'joins': re.compile('[- /]')
    , 'whitespace': re.compile('\s+')
    , 'punctuation': re.compile('[+\-*/=\$%^&\'",.:;?{()}#<>\[\]]')
    , 'repeated_underscore': re.compile('_{2,}')
    }

########################
###   REGISTER
########################

class TokeniserCodec(object):
    def __init__(self, tokeniser):
        self.tokeniser = tokeniser
    
    def register(self):
        class StreamReader(utf_8.StreamReader):
            # Normal python uses StreamRader
            def __init__(sr, stream, *args, **kwargs):
                codecs.StreamReader.__init__(sr, stream, *args, **kwargs)
                data = self.dealwith(sr.stream.readline)
                sr.stream = cStringIO.StringIO(data)
        
        def decode(text, *args):
            # pypy uses decode
            utf8 = encodings.search_function('utf8') # Assume utf8 encoding
            reader = utf8.streamreader(cStringIO.StringIO(text))
            data = self.dealwith(reader.readline)
            return unicode(data), len(data)

        def searchFunction(s):
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

        codecs.register(searchFunction)
    
    def dealwith(readline):
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
            data = untokenize(data)
        
        return data
        
    def outputForDebugging(stream, data):
        """It will write the translated version of the file"""
        with open('%s.spec.out' % stream.name, 'w') as f: f.write(data)

########################
###   Tokeniser
########################

class Tokeniser(object):

    def __init__(self
        , defaultKls='object', extraImports=None, withDefaultImports=True
        , withDescribeAttrs=True, withoutShouldDsl=False
        ):
        self.withDefaultImports = withDefaultImports
        self.withDescribeAttrs = withDescribeAttrs
        self.withoutShouldDsl = withoutShouldDsl
        self.defaultImports = self.determineImports(extraImports)
        self.defaultKls = self.tokensIn(defaultKls)
        self.constructReplacements()

    ########################
    ###   UTILITY
    ########################
                
    def recordName(self, record, describeStack, use, cleaned, english):
        if cleaned.replace("_", " ") != english[1:-1]:
            kls = None
            if describeStack:
                kls = describeStack[-1][1]
            v = record.get(kls, [])
            v.append((use, english))
            record[kls] = v

    def determineImports(self, extra):
        default = []

        if extra:
            if type(extra) in (str, unicode):
                default.extend(self.tokensIn(extra))
            else:
                for d in extra:
                    if d[0] == NEWLINE:
                        # I want to make sure the extra imports don't 
                        # Take up extra lines in the code than the "# coding: spec"
                        default.append((OP, ';'))
                    else:
                        default.append(d)

        if self.withDefaultImports:
            if default and tuple(default[-1]) != (OP, ';'):
                default.append((OP, ';'))

            should_dsl = "from should_dsl import *;"
            if self.withoutShouldDsl:
                should_dsl = ""
            
            default.extend(
                self.tokensIn('import nose; from nose.tools import *; %s from noseOfYeti.noy_helper import *;' % should_dsl)
            )

        return default

    def acceptable(self, value, capitalize=False):
        name = regexes['punctuation'].sub("", regexes['joins'].sub("_", value))
        # Clean up irregularities in underscores.
        name = regexes['repeated_underscore'].sub("_", name.strip('_'))
        if capitalize:
            # We don't use python's built in capitalize method here because it
            # turns all upper chars into lower chars if not at the start of
            # the string and we only want to change the first character.
            name_parts = []
            for word in name.split('_'):
                name_parts.append(word[0].upper())
                if len(word) > 1:
                    name_parts.append(word[1:])
            name = ''.join(name_parts)
        return name

    def tokensIn(self, s, strip_it=True):
        self.taken = False
        def get():
            #Making generate_tokens not loop forever
            if not self.taken:
                self.taken = True
                if strip_it:
                    return s.strip()
                else:
                    return s
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
            , (OP, '(')
            , (NAME, 'self')
            , (OP, ')')
            ]

        self.after_each = [
              (NAME, 'def')
            , (NAME, self.getEquivalence('after_each'))
            , (OP, '(')
            , (NAME, 'self')
            , (OP, ')')
            ]

        self.testSkip = [
              (OP, ':')
            , (NAME, 'raise')
            , (NAME, 'nose.SkipTest')
            ]

        self.endIt = [ (OP, ')')]

    def startFunction(self, funcName, withSelf=True):
        lst =  [
              (NAME, funcName)
            , (OP, '(')
            ]

        if withSelf:
            lst.append((NAME, 'self'))

        return lst

    def makeDescribe(self, value, nextDescribeKls, inheriting=False):
        name = self.acceptable(value, True)
        if nextDescribeKls and inheriting:
            use = nextDescribeKls
            if use.startswith('Test'):
                use = use[4:]
            name = 'Test{0}_{1}'.format(use, name)
        else:
            name = 'Test{0}'.format(name)

        result = [ (NAME, name)
                 , (OP, '(')
                 ]
        if nextDescribeKls:
            result.extend(self.tokensIn(nextDescribeKls))
        else:
            result.extend(self.defaultKls)
        result.append((OP, ')'))
        return result, name

    def makeSuper(self, nextDescribeKls, method):
        if nextDescribeKls:
            kls = self.tokensIn(nextDescribeKls)
        else:
            kls = self.defaultKls

        result = [ (NAME, 'noy_sup_%s' % self.getEquivalence(method))
                 , (OP, '(')
                 , (NAME, 'super')
                 , (OP, '(')
                 ]

        result.extend(kls)

        result.extend(
            [ (OP, ',')
            , (NAME, 'self')
            , (OP, ')')
            , (OP, ')')
            , (OP, ';')
            ]
        )

        return result

    def makeDescribeAttr(self, describe):
        return [ (NEWLINE, '\n')
               , (NAME, describe)
               , (OP, '.')
               , (NAME, 'is_noy_spec')
               , (OP, '=')
               , (NAME, 'True')
               ]
   
    def makeNameModifier(self, kls, cleaned, english):
        result = [ (NEWLINE, '\n') ]
        
        if kls:
            result.extend(
                [ (NAME, kls)
                , (OP, '.')
                ]
            )

        result.append((NAME, cleaned))

        if kls:
            result.extend(
                [ (OP, '.')
                , (NAME, "__func__")
                ]
            )

        result.extend(
            [ (OP, '.')
            , (NAME, "__testname__")
            , (OP, '=')
            , (STRING, english)
            ]
        )
        
        return result

    ########################
    ###   TRANSLATE
    ########################

    def translate(self, readline, result=None):
        if result is None:
            result = []

        result.extend([d for d in self.defaultImports])

        currentDescribeLevel = 0

        nextDescribeKls = None
        adjustIndentAt = []
        describeStack = []
        indentAmounts = []
        keepLastToken = False
        startingAnIt = False
        allDescribes = []
        methodNames = {}
        argsForIt = []

        skippedTest = True
        lookAtSpace = False
        afterSpace = True
        justAppend = False
        indentType = ' '
        ignoreNext = None
        groupStack = []
        lastToken = ' '
        endedIt = False
        emptyDescr = False

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
                        indentAmounts.append(scol)

                    # Dedenting describes removes them from being inheritable
                    while describeStack and describeStack[-1][0] >= scol:
                        describeStack.pop()

                    if not describeStack:
                        currentDescribeLevel = 0

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
                result.extend(self.endIt)
                endedIt = True

            # Determining what to replace and with what ::
            if lastToken in ('describe', 'context'):
                if tokenum == NAME or (tokenum == OP and value == '.'): # inherited class
                    if nextDescribeKls is None:
                        nextDescribeKls = value
                    else:
                        nextDescribeKls += value
                    keepLastToken = True

                elif tokenum == STRING: # the described object
                    inheritance = False
                    if describeStack:
                        if not nextDescribeKls:
                            inheritance = True
                            nextDescribeKls = describeStack[-1][1]

                    res, name = self.makeDescribe(value, nextDescribeKls, inheritance)
                    describeStack.append([currentDescribeLevel, name])
                    allDescribes.append(name)

                    result.extend(res)

            elif tokenum == OP:
                if value in ['(', '[', '{']:
                    # add to the stack because we started a list
                    groupStack.append(value)
                    emptyDescr = False

                elif value in [')', ']', '}']:
                    # not necessary to check for correctness
                    groupStack.pop()

                justAppend = True
                if value == ',' and startingAnIt and not len(describeStack) and not len(argsForIt):
                    justAppend = False

            elif afterSpace and tokenum == NAME:
                if value in ('describe', 'context'):
                    # Make sure we dedent if we just made a skip test
                    if skippedTest:
                        result.append((INDENT, indentType * (scol - currentDescribeLevel)))
                        skippedTest = False

                    # Make sure we insert a pass if we inserted an empty describe.
                    if emptyDescr and scol > currentDescribeLevel:
                        while result[-1][0] in (INDENT, NEWLINE):
                            result.pop()
                        result.append((NAME, 'pass'))
                        result.append((NEWLINE, '\n'))
                        result.append((INDENT, indentType * scol))

                    emptyDescr = True

                    currentDescribeLevel = scol
                    nextDescribeKls = None

                    # Making sure this line starts at the beginning
                    # By editing previous INDENT
                    if result and result[-1][0] == INDENT:
                        result[-1] = (INDENT, result[-1][1][currentDescribeLevel:])

                    result.append((NAME, 'class'))

                elif value in ('it', 'ignore'):
                    skippedTest = False
                    emptyDescr = False
                    result.append((NAME, 'def'))

                elif value in ('before_each', 'after_each'):
                    skippedTest = False
                    emptyDescr = False
                    result.extend(getattr(self, value))
                    if describeStack:
                        expecting = [ (OP, ':')
                                    , (NEWLINE, '\n')
                                    ]

                        result.extend(expecting)
                        ignoreNext = expecting

                        adjustIndentAt.append(len(result))
                        result.append((INDENT, ''))
                        result.extend(self.makeSuper(describeStack[-1][1], value))

                else:
                    skippedTest = False
                    emptyDescr = False
                    justAppend = True
                    if startingAnIt:
                        argsForIt.append(value)

            elif tokenum == STRING:
                if lastToken == 'it':
                    endedIt = False
                    argsForIt = []
                    startingAnIt = True
                    cleaned = self.acceptable(value)
                    funcName = "test_%s" % cleaned
                    result.extend(self.startFunction(funcName, withSelf=len(describeStack)))
                    self.recordName(methodNames, describeStack, funcName, cleaned, value)

                elif lastToken == 'ignore':
                    endedIt = False
                    argsForIt = []
                    startingAnIt = True
                    cleaned = self.acceptable(value)
                    funcName = "ignore__%s" % cleaned
                    result.extend(self.startFunction(funcName, withSelf=len(describeStack)))
                    self.recordName(methodNames, describeStack, funcName, cleaned, value)

                else:
                    emptyDescr = False
                    justAppend = True

            elif tokenum == NEWLINE and lastToken != ':' and startingAnIt:
                result.extend(self.testSkip)
                startingAnIt = False
                skippedTest = True
                justAppend = True

            else:
                if tokenum == NAME and startingAnIt:
                    argsForIt.append(value)
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
            if keepLastToken:
                keepLastToken = False
            else:
                lastToken = value

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
            result.append((NEWLINE, '\n'))
            result.append((INDENT, ''))

            for describe in allDescribes:
                result.extend(self.makeDescribeAttr(describe))
        
        for kls, names in methodNames.items():
            for cleaned, english in names:
                result.extend(self.makeNameModifier(kls, cleaned, english))

        return result
