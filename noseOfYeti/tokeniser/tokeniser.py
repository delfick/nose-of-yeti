from tokenize import NAME, OP, INDENT, NEWLINE, DEDENT, STRING, ERRORTOKEN
from tokenize import generate_tokens
from tokens import Tokens, tokensIn
import re

regexes = {
      'joins': re.compile('[- /]')
    , 'whitespace': re.compile('\s+')
    , 'punctuation': re.compile('[+\-*/=\$%^&\'",.:;?{()}#<>\[\]]')
    , 'repeated_underscore': re.compile('_{2,}')
    }

class Tracker(object):
    def __init__(self, result, tokens):
        self.currentDescribeLevel = 0

        self.nextDescribeKls = None
        self.adjustIndentAt = []
        self.describeStack = []
        self.indentAmounts = []
        self.keepLastToken = False
        self.startingAnIt = False
        self.allDescribes = []
        self.methodNames = {}
        self.argsForIt = []

        self.skippedTest = True
        self.lookAtSpace = False
        self.afterSpace = True
        self.justAppend = False
        self.indentType = ' '
        self.ignoreNext = None
        self.groupStack = []
        self.lastToken = ' '
        self.endedIt = False
        self.emptyDescr = False
        self.nextIgnore = None
        
        if result is None:
            result = []
        self.result = result
        self.tokens = tokens

    ########################
    ###   UTILITY
    ########################

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
    ###   TRACK
    ########################
    
    def nameForGroup(self):
        return self.lastToken in ('describe', 'context')
                
    def recordName(self, record, use, cleaned, english):
        if cleaned.replace("_", " ") != english[1:-1]:
            kls = None
            if self.describeStack:
                kls = self.describeStack[-1][1]
            v = record.get(kls, [])
            v.append((use, english))
            record[kls] = v
    
    def ignore_token(self, tokenum, value):
        if self.ignoreNext:
            nextIgnore = self.ignoreNext
            if type(self.ignoreNext) is list:
                nextIgnore = self.ignoreNext.pop(0)

            if nextIgnore == (tokenum, value):
                return True
            else:
                self.nextIgnore = None
                return False
                
    def inheritedClass(self, value):
        if self.nextDescribeKls is None:
            self.nextDescribeKls = value
        else:
            self.nextDescribeKls += value
        self.keepLastToken = True
    
    def nameDescribe(self, value):
        inheritance = False
        if self.describeStack:
            if not self.nextDescribeKls:
                inheritance = True
                self.nextDescribeKls = self.describeStack[-1][1]

        res, name = self.tokens.makeDescribe(self.acceptable(value, True), value, self.nextDescribeKls, inheritance)
        self.describeStack.append([self.currentDescribeLevel, name])
        self.allDescribes.append(name)

        self.result.extend(res)
                
    def next_token(self, tokenum, value):
        # By default, we don't just append the value
        self.justAppend = False

        # Determine if working with spaces or tabs
        if tokenum == INDENT:
            self.indentType = value[0]
            
    def closing_an_it(self, tokenum, value):
        #Determine if we have an it to close
        return self.startingAnIt and not self.endedIt and (value == ":" or tokenum == NEWLINE)
    
    def close_it(self):
        self.result.extend(self.tokens.endIt)
        self.endedIt = True
        
    def determineIndentation(self, tokenum, scol):
        if self.afterSpace and tokenum not in (NEWLINE, DEDENT, INDENT):
            if not self.groupStack:
                # We don't care about indentation inside a group (list, tuple or dictionary)
                if not self.indentAmounts or scol > self.indentAmounts[-1]:
                    self.indentAmounts.append(scol)

                # Dedenting describes removes them from being inheritable
                while self.describeStack and self.describeStack[-1][0] >= scol:
                    self.describeStack.pop()

                if not self.describeStack:
                    self.currentDescribeLevel = 0

                while self.adjustIndentAt:
                    self.result[self.adjustIndentAt.pop()] = (INDENT, self.indentType * (scol - self.currentDescribeLevel))
            
    def convertDedent(self):
        # Dedent means go back to last indentation
        if self.indentAmounts:
            self.indentAmounts.pop()

        # Change the token
        tokenum = INDENT

        # Get last indent amount
        lastIndent = 0
        if self.indentAmounts:
            lastIndent = self.indentAmounts[-1]

        # Make sure we don't have multiple indents in a row
        if self.result[-1][0] == INDENT:
            self.result.pop()

        value = self.indentType * lastIndent
        return tokenum, value
            
    def foundOperator(self, value):
        if value in ['(', '[', '{']:
            # add to the stack because we started a list
            self.groupStack.append(value)
            self.emptyDescr = False

        elif value in [')', ']', '}']:
            # not necessary to check for correctness
            self.groupStack.pop()

        self.justAppend = True
        if value == ',' and self.startingAnIt and not len(self.describeStack) and not len(self.argsForIt):
            self.justAppend = False
    
    def nameAfterSpace(self, tokenum):
        return self.afterSpace and tokenum == NAME
    
    def beginTest(self):
        self.skippedTest = False
        self.emptyDescr = False
        self.result.append((NAME, 'def'))
    
    def beginGroup(self, scol):
        # Make sure we dedent if we just made a skip test
        if self.skippedTest:
            self.result.append((INDENT, self.indentType * (scol - self.currentDescribeLevel)))
            self.skippedTest = False

        # Make sure we insert a pass if we inserted an empty describe.
        if self.emptyDescr and scol > self.currentDescribeLevel:
            while self.result[-1][0] in (INDENT, NEWLINE):
                self.result.pop()
            self.result.append((NAME, 'pass'))
            self.result.append((NEWLINE, '\n'))
            self.result.append((INDENT, self.indentType * scol))

        self.emptyDescr = True

        self.currentDescribeLevel = scol
        self.nextDescribeKls = None

        # Making sure this line starts at the beginning
        # By editing previous INDENT
        if self.result and self.result[-1][0] == INDENT:
            self.result[-1] = (INDENT, self.result[-1][1][self.currentDescribeLevel:])

        self.result.append((NAME, 'class'))
                
    def beginTestAdmin(self, value):
        self.skippedTest = False
        self.emptyDescr = False
        self.result.extend(getattr(self.tokens, value))
        if self.describeStack:
            expecting = [ (OP, ':')
                        , (NEWLINE, '\n')
                        ]

            self.result.extend(expecting)
            self.ignoreNext = expecting

            self.adjustIndentAt.append(len(self.result))
            self.result.append((INDENT, ''))
            self.result.extend(self.tokens.makeSuper(self.describeStack[-1][1], value))
                
    def unknownNameAfterSpace(self, value):
        self.skippedTest = False
        self.emptyDescr = False
        self.justAppend = True
        if self.startingAnIt:
            self.argsForIt.append(value)
            
    def addString(self, value):
        if self.lastToken in ('it', 'ignore'):
            if self.lastToken == 'it':
                prefix = 'test'
            else:
                prefix = 'ignore_'
            
            self.endedIt = False
            self.argsForIt = []
            self.startingAnIt = True
            cleaned = self.acceptable(value)
            funcName = "%s_%s" % (prefix, cleaned)
            self.result.extend(self.tokens.startFunction(funcName, withSelf=len(self.describeStack)))
            self.recordName(self.methodNames, funcName, cleaned, value)

        else:
            self.emptyDescr = False
            self.justAppend = True
            
    def ignoringTest(self, tokenum):
        return tokenum == NEWLINE and self.lastToken != ':' and self.startingAnIt
    
    def ignoreTest(self):
        self.result.extend(self.tokens.testSkip)
        self.startingAnIt = False
        self.skippedTest = True
        self.justAppend = True
            
    def defaultAction(self, tokenum, value):
        if tokenum == NAME and self.startingAnIt:
            self.argsForIt.append(value)
        if tokenum == NEWLINE and self.lastToken == ':' and self.startingAnIt:
            self.startingAnIt = False
        if tokenum not in (NEWLINE, INDENT):
            self.emptyDescr = False
        self.justAppend = True
    
    def appendToken(self, tokenum, value):
        if self.justAppend:
            v = value

            # First ensure, the indentation has been normalised (incase of nesting)
            if tokenum == INDENT and self.currentDescribeLevel > 0:
                v = value[self.currentDescribeLevel:]

            self.result.append([tokenum, v])
        
        # Storing current token if allowed to
        if self.keepLastToken:
            self.keepLastToken = False
        else:
            self.lastToken = value
        
    def isWhitespace(self, tokenum, value):
        if value == '\n':
            self.afterSpace = True
            self.lookAtSpace = True

        else:
            self.afterSpace = False
            if self.lookAtSpace and (value == '' or regexes['whitespace'].match(value)):
                self.afterSpace = True

                if tokenum != INDENT:
                    # Only want to count at the beginning of the line
                    # Isn't reset till we have a newline
                    self.lookAtSpace = False
    
    def skipTestIfNecessary(self):
        if self.startingAnIt and not self.endedIt:
            self.result.extend(self.tokens.endIt)
            if self.lastToken != ':':
                self.result.extend(self.tokens.testSkip)
    
    def removeTrailingIndents(self):
        while self.result and self.result[-2][0] in (INDENT, ERRORTOKEN, NEWLINE):
            self.result.pop(-2)
    
    def addDescribeAttrs(self):
        if self.allDescribes:
            self.result.append((NEWLINE, '\n'))
            self.result.append((INDENT, ''))

            for describe in self.allDescribes:
                self.result.extend(self.tokens.makeDescribeAttr(describe))
    
    def addMethodNames(self):
        for kls, names in self.methodNames.items():
            for cleaned, english in names:
                self.result.extend(self.tokens.makeNameModifier(kls, cleaned, english))

class Tokeniser(object):
    def __init__(self, defaultKls='object', withDescribeAttrs=True, importTokens=None):
        self.tokens = Tokens(defaultKls)
        self.importTokens = importTokens
        self.withDescribeAttrs = withDescribeAttrs

    ########################
    ###   TRANSLATE
    ########################

    def translate(self, readline, result=None):
        # Tracker to keep track of information as the file is processed
        self.tracker = Tracker(result, self.tokens)
        
        if self.importTokens:
            self.tracker.result.extend([d for d in self.importTokens])

        # Looking at all the tokens
        for tokenum, value, (_, scol), _, _ in generate_tokens(readline):
            # Determine if we need to ignore this value
            if self.tracker.ignore_token(tokenum, value):
                continue
            
            self.tracker.next_token(tokenum, value)
            
            # Ensuring NEWLINE tokens are actually specified as such
            if tokenum != NEWLINE and value == '\n':
                tokenum = NEWLINE
            
            # Determine next level of indentation
            self.tracker.determineIndentation(tokenum, scol)

            # I want to change dedents into indents, because they seem to screw nesting up
            if tokenum == DEDENT:
                tokenum, value = self.tracker.convertDedent()
            
            if self.tracker.closing_an_it(tokenum, value):
                self.tracker.close_it()

            # Determining what to replace and with what ::
            if self.tracker.nameForGroup():
                if tokenum == NAME or (tokenum == OP and value == '.'):
                    self.tracker.inheritedClass(value)

                elif tokenum == STRING:
                    self.tracker.nameDescribe(value)

            elif tokenum == OP:
                self.tracker.foundOperator(value)
            
            elif self.tracker.nameAfterSpace(tokenum):
                if value in ('describe', 'context'):
                    self.tracker.beginGroup(scol)
                    
                elif value in ('it', 'ignore'):
                    self.tracker.beginTest()

                elif value in ('before_each', 'after_each'):
                    self.tracker.beginTestAdmin(value)

                else:
                    self.tracker.unknownNameAfterSpace(value)

            elif tokenum == STRING:
                self.tracker.addString(value)

            elif self.tracker.ignoringTest(tokenum):
                self.tracker.ignoreTest()

            else:
                self.tracker.defaultAction(tokenum, value)

            # Just apending if token isn't replaced and should be kept
            self.tracker.appendToken(tokenum, value)

            # Determining if this token is whitespace at the beginning of the line so next token knows
            self.tracker.isWhitespace(tokenum, value)
        
        self.tracker.skipTestIfNecessary()

        # Remove trailing indents and dedents
        self.tracker.removeTrailingIndents()

        # Add attributes to our Describes so that the plugin can handle some nesting issues
        # Where we have tests in upper level describes being run in lower level describes
        if self.withDescribeAttrs:
            self.tracker.addDescribeAttrs()
        
        self.tracker.addMethodNames()
        return self.tracker.result
