from tokenize import NAME, OP, INDENT, NEWLINE, DEDENT, STRING, ERRORTOKEN
from tokens import Tokens
import re

regexes = {
      'joins': re.compile('[- /]')
    , 'whitespace': re.compile('\s+')
    , 'punctuation': re.compile('[+\-*/=\$%^&\'",.:;?{()}#<>\[\]]')
    , 'repeated_underscore': re.compile('_{2,}')
    }

class Tokeniser(object):

    def __init__(self
        , defaultKls='object', extraImports=None, withDefaultImports=True
        , withDescribeAttrs=True, withoutShouldDsl=False
        ):
        self.tokens = Tokens(defaultKls)
        self.defaultKls = self.tokens.defaultKls
        self.withDefaultImports = withDefaultImports
        self.withDescribeAttrs = withDescribeAttrs
        self.withoutShouldDsl = withoutShouldDsl
        self.defaultImports = self.determineImports(extraImports)
        self.tokens.constructReplacements()

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
                default.extend(self.tokens.tokensIn(extra))
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
                self.tokens.tokensIn('import nose; from nose.tools import *; %s from noseOfYeti.noy_helper import *;' % should_dsl)
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
        for tokenum, value, (_, scol), (_, ecol), _ in self.tokens.generate(readline):
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
                result.extend(self.tokens.endIt)
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

                    res, name = self.tokens.makeDescribe(self.acceptable(value, True), value, nextDescribeKls, inheritance)
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
                    result.extend(getattr(self.tokens, value))
                    if describeStack:
                        expecting = [ (OP, ':')
                                    , (NEWLINE, '\n')
                                    ]

                        result.extend(expecting)
                        ignoreNext = expecting

                        adjustIndentAt.append(len(result))
                        result.append((INDENT, ''))
                        result.extend(self.tokens.makeSuper(describeStack[-1][1], value))

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
                    result.extend(self.tokens.startFunction(funcName, withSelf=len(describeStack)))
                    self.recordName(methodNames, describeStack, funcName, cleaned, value)

                elif lastToken == 'ignore':
                    endedIt = False
                    argsForIt = []
                    startingAnIt = True
                    cleaned = self.acceptable(value)
                    funcName = "ignore__%s" % cleaned
                    result.extend(self.tokens.startFunction(funcName, withSelf=len(describeStack)))
                    self.recordName(methodNames, describeStack, funcName, cleaned, value)

                else:
                    emptyDescr = False
                    justAppend = True

            elif tokenum == NEWLINE and lastToken != ':' and startingAnIt:
                result.extend(self.tokens.testSkip)
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
            result.extend(self.tokens.endIt)
            if lastToken != ':':
                result.extend(self.tokens.testSkip)

        # Remove trailing indents and dedents
        while result and result[-2][0] in (INDENT, ERRORTOKEN, NEWLINE):
            result.pop(-2)

        # Add attributes to our Describes so that the plugin can handle some nesting issues
        # Where we have tests in upper level describes being run in lower level describes
        if self.withDescribeAttrs and allDescribes:
            result.append((NEWLINE, '\n'))
            result.append((INDENT, ''))

            for describe in allDescribes:
                result.extend(self.tokens.makeDescribeAttr(describe))
        
        for kls, names in methodNames.items():
            for cleaned, english in names:
                result.extend(self.tokens.makeNameModifier(kls, cleaned, english))

        return result
