from tokenize import NAME, OP, INDENT, NEWLINE, DEDENT, STRING, ERRORTOKEN
from contextlib import contextmanager
from tokenize import generate_tokens
from tokens import Tokens, tokensIn
import re

regexes = {
      'joins': re.compile('[- /]')
    , 'whitespace': re.compile('\s+')
    , 'punctuation': re.compile('[+\-*/=\$%^&\'",.:;?{()}#<>\[\]]')
    , 'repeated_underscore': re.compile('_{2,}')
    }

class TokenDetails(object):
    def __init__(self, tokenum=None, value=None, scol=0):
        self.set(tokenum, value, scol)
    
    def set(self, tokenum, value, scol):
        self.scol = scol
        self.value = value
        self.tokenum = tokenum
    
    def transfer(self, details):
        details.set(self.tokenum, self.value, self.scol)

class Tracker(object):
    def __init__(self, result, defaultKls='object'):
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
        self.endedIt = False
        self.emptyDescr = False
        self.nextIgnore = None
        
        if result is None:
            result = []
        self.result = result
        self.tokens = Tokens(defaultKls)
        
        self._last = TokenDetails(value=' ')
        self._current = TokenDetails()
    
    @property
    def last(self):
        return self._last
    
    @property
    def current(self):
        return self._current
    
    @current.setter
    def current(self, values):
        self.justAppend = False
        
        if self.current.tokenum == INDENT and self.current.value:
            self.indentType = self.current.value[0]
        
        if not self.keepLastToken:
            self._current.transfer(self._last)
        else:
            # Reset keepLastToken
            self.keepLastToken = False
        
        self._current.set(*values)
    
    @contextmanager
    def add_phase(self):
        yield self
        
        # Last thing may have beeen a skippable test
        self.skipTestIfNecessary()

        # Remove trailing indents and dedents
        while self.result and self.result[-2][0] in (INDENT, ERRORTOKEN, NEWLINE):
            self.result.pop(-2)
    
    def next_token(self, tokenum, value, scol):
        self.current = (tokenum, value, scol)
        if not self.ignore_token():
            self.determineIndentation()
            
            if self.closing_an_it():
                self.close_it()
            
            self.progress()
            
            # Just apending if token isn't replaced and should be kept
            if self.justAppend:
                self.appendToken()
            
            # Determining if this token is whitespace at the beginning of the line so next token knows
            self.isWhitespace()

    ########################
    ###   UTILITY
    ########################
        
    def addTokens(self, tokens):
        self.result.extend([d for d in tokens])
            
    def closing_an_it(self):
        #Determine if we have an it to close
        return self.startingAnIt and not self.endedIt and (self.current.value == ":" or self.current.tokenum == NEWLINE)
                
    def recordName(self, record, use, cleaned, english):
        if cleaned.replace("_", " ") != english[1:-1]:
            kls = None
            if self.describeStack:
                kls = self.describeStack[-1][1]
            v = record.get(kls, [])
            v.append((use, english))
            record[kls] = v
    
    def makeMethodNames(self):
        result = []
        for kls, names in self.methodNames.items():
            for cleaned, english in names:
                result.extend(self.tokens.makeNameModifier(kls, cleaned, english))
        return result
                
    def nameNextGroupKls(self):
        if self.nextDescribeKls is None:
            self.nextDescribeKls = self.current.value
        else:
            self.nextDescribeKls += self.current.value
        
    def determineKlsForGroup(self):
        inheritance = False
        if not self.nextDescribeKls:
            if self.describeStack:
                inheritance = True
                self.nextDescribeKls = self.describeStack[-1][1]
        
        return inheritance
    
    def makeDescribeAttrs(self):
        result = []
        if self.allDescribes:
            result.append((NEWLINE, '\n'))
            result.append((INDENT, ''))

            for describe in self.allDescribes:
                result.extend(self.tokens.makeDescribeAttr(describe))
        
        return result

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
            
    def progress(self):
        # Determining what to replace and with what
        if self.last.value in ('describe', 'context'):
            self.foundGroupName()

        elif self.current.tokenum == OP:
            self.foundOperator()
        
        elif self.afterSpace and self.current.tokenum == NAME:
            self.dealWithNameAfterSpace()

        elif self.current.tokenum == STRING:
            self.addString()

        elif self.current.tokenum == NEWLINE and self.last.value != ':' and self.startingAnIt:
            self.ignoreTest()

        else:
            tokenum, value = self.current.tokenum, self.current.value
            
            if tokenum == NAME and self.startingAnIt:
                self.argsForIt.append(value)
            if tokenum == NEWLINE and self.last.value == ':' and self.startingAnIt:
                self.startingAnIt = False
            if tokenum not in (NEWLINE, INDENT):
                self.emptyDescr = False
            
            self.justAppend = True
    
    def ignore_token(self):
        if self.ignoreNext:
            nextIgnore = self.ignoreNext
            if type(self.ignoreNext) is list:
                nextIgnore = self.ignoreNext.pop(0)

            if nextIgnore == (self.current.tokenum, self.current.value):
                return True
            else:
                self.nextIgnore = None
                return False
    
    def nameGroup(self):
        # Get english and python name for group
        english = self.current.value
        pythonName = self.acceptable(english, True)
        
        # Determine kls for group
        inheritance = self.determineKlsForGroup()
        
        # Create and add tokens
        res, name = self.tokens.makeDescribe(pythonName, english, self.nextDescribeKls, inheritance)
        self.describeStack.append([self.currentDescribeLevel, name])
        self.allDescribes.append(name)
        self.result.extend(res)
    
    def close_it(self):
        self.result.extend(self.tokens.endIt)
        self.endedIt = True
        
    def determineIndentation(self):
        
        # Ensuring NEWLINE tokens are actually specified as such
        if self.current.tokenum != NEWLINE and self.current.value == '\n':
            self.current.tokenum = NEWLINE
        
        if self.afterSpace and self.current.tokenum not in (NEWLINE, DEDENT, INDENT):
            if not self.groupStack:
                # We don't care about indentation inside a group (list, tuple or dictionary)
                if not self.indentAmounts or self.current.scol > self.indentAmounts[-1]:
                    self.indentAmounts.append(self.current.scol)

                # Dedenting describes removes them from being inheritable
                while self.describeStack and self.describeStack[-1][0] >= self.current.scol:
                    self.describeStack.pop()

                if not self.describeStack:
                    self.currentDescribeLevel = 0

                while self.adjustIndentAt:
                    self.result[self.adjustIndentAt.pop()] = (INDENT, self.indentType * (self.current.scol - self.currentDescribeLevel))
        
        # I want to change dedents into indents, because they seem to screw nesting up
        if self.current.tokenum == DEDENT:
            self.current.tokenum, self.current.value = self.convertDedent()
            
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
            
    def foundOperator(self):
        if self.current.value in ['(', '[', '{']:
            # add to the stack because we started a list
            self.groupStack.append(self.current.value)
            self.emptyDescr = False

        elif self.current.value in [')', ']', '}']:
            # not necessary to check for correctness
            self.groupStack.pop()

        self.justAppend = True
        if self.current.value == ',' and self.startingAnIt and not len(self.describeStack) and not len(self.argsForIt):
            self.justAppend = False
    
    def beginTest(self):
        self.skippedTest = False
        self.emptyDescr = False
        self.result.append((NAME, 'def'))
    
    def beginGroup(self):
        # Make sure we dedent if we just made a skip test
        if self.skippedTest:
            self.result.append((INDENT, self.indentType * (self.current.scol - self.currentDescribeLevel)))
            self.skippedTest = False

        # Make sure we insert a pass if we inserted an empty describe.
        if self.emptyDescr and self.current.scol > self.currentDescribeLevel:
            while self.result[-1][0] in (INDENT, NEWLINE):
                self.result.pop()
            self.result.append((NAME, 'pass'))
            self.result.append((NEWLINE, '\n'))
            self.result.append((INDENT, self.indentType * self.current.scol))

        self.emptyDescr = True

        self.currentDescribeLevel = self.current.scol
        self.nextDescribeKls = None

        # Making sure this line starts at the beginning
        # By editing previous INDENT
        if self.result and self.result[-1][0] == INDENT:
            self.result[-1] = (INDENT, self.result[-1][1][self.currentDescribeLevel:])

        self.result.append((NAME, 'class'))
                
    def beginTestAdmin(self):
        self.skippedTest = False
        self.emptyDescr = False
        self.result.extend(getattr(self.tokens, self.current.value))
        if self.describeStack:
            expecting = [ (OP, ':')
                        , (NEWLINE, '\n')
                        ]

            self.result.extend(expecting)
            self.ignoreNext = expecting

            self.adjustIndentAt.append(len(self.result))
            self.result.append((INDENT, ''))
            self.result.extend(self.tokens.makeSuper(self.describeStack[-1][1], self.current.value))
                
    def unknownNameAfterSpace(self):
        self.skippedTest = False
        self.emptyDescr = False
        self.justAppend = True
        if self.startingAnIt:
            self.argsForIt.append(self.current.value)
            
    def addString(self):
        if self.last.value in ('it', 'ignore'):
            if self.last.value == 'it':
                prefix = 'test'
            else:
                prefix = 'ignore_'
            
            self.endedIt = False
            self.argsForIt = []
            self.startingAnIt = True
            cleaned = self.acceptable(self.current.value)
            funcName = "%s_%s" % (prefix, cleaned)
            self.result.extend(self.tokens.startFunction(funcName, withSelf=len(self.describeStack)))
            self.recordName(self.methodNames, funcName, cleaned, self.current.value)

        else:
            self.emptyDescr = False
            self.justAppend = True
    
    def ignoreTest(self):
        self.result.extend(self.tokens.testSkip)
        self.startingAnIt = False
        self.skippedTest = True
        self.justAppend = True
    
    def appendToken(self):
        v = self.current.value

        # First ensure, the indentation has been normalised (incase of nesting)
        if self.current.tokenum == INDENT and self.currentDescribeLevel > 0:
            v = self.current.value[self.currentDescribeLevel:]

        self.result.append([self.current.tokenum, v])
        
    def isWhitespace(self):
        if self.current.value == '\n':
            self.afterSpace = True
            self.lookAtSpace = True

        else:
            self.afterSpace = False
            if self.lookAtSpace and (self.current.value == '' or regexes['whitespace'].match(self.current.value)):
                self.afterSpace = True

                if self.current.tokenum != INDENT:
                    # Only want to count at the beginning of the line
                    # Isn't reset till we have a newline
                    self.lookAtSpace = False
    
    def skipTestIfNecessary(self):
        if self.startingAnIt and not self.endedIt:
            self.result.extend(self.tokens.endIt)
            if self.last.value != ':':
                self.result.extend(self.tokens.testSkip)
            
    def foundGroupName(self):
        if self.current.tokenum == NAME or (self.current.tokenum == OP and self.current.value == '.'):
            self.nameNextGroupKls()
            self.keepLastToken = True

        elif self.current.tokenum == STRING:
            self.nameGroup()
            
    def dealWithNameAfterSpace(self):
        value = self.current.value
        if value in ('describe', 'context'):
            self.beginGroup()
            
        elif value in ('it', 'ignore'):
            self.beginTest()

        elif value in ('before_each', 'after_each'):
            self.beginTestAdmin()

        else:
            self.unknownNameAfterSpace()

class Tokeniser(object):
    def __init__(self, defaultKls='object', withDescribeAttrs=True, importTokens=None):
        self.defaultKls = defaultKls
        self.importTokens = importTokens
        self.withDescribeAttrs = withDescribeAttrs

    ########################
    ###   TRANSLATE
    ########################

    def translate(self, readline, result=None):
        # Tracker to keep track of information as the file is processed
        self.tracker = Tracker(result, self.defaultKls)
        
        # Add import stuff at the top of the file
        if self.importTokens:
            self.tracker.addTokens(self.importTokens)

        # Looking at all the tokens
        with self.tracker.add_phase() as tracker:
            for tokenum, value, (_, scol), _, _ in generate_tokens(readline):
                self.tracker.next_token(tokenum, value, scol)

        # Add attributes to our Describes so that the plugin can handle some nesting issues
        # Where we have tests in upper level describes being run in lower level describes
        if self.withDescribeAttrs:
            self.tracker.addTokens(self.tracker.makeDescribeAttrs())
        
        # Add lines to bottom of file to add __testname__ attributes
        self.tracker.addTokens(self.tracker.makeMethodNames())
        
        # Return translated list of tokens
        return self.tracker.result
