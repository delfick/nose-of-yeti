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

def acceptable(value, capitalize=False):
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

class TokenDetails(object):
    def __init__(self, tokenum=None, value=None, scol=0):
        self.set(tokenum, value, scol)
    
    def set(self, tokenum, value, scol):
        self.scol = scol
        self.value = value
        self.tokenum = tokenum
    
    def transfer(self, details):
        details.set(self.tokenum, self.value, self.scol)
        
class Single(object):
    def __init__(self, typ=None, group=None, indent=0):
        self.typ = typ
        self.args = []
        self.group = group
        self.indent = indent
        self.skipped = False
        self.isIgnore = typ == 'ignore'
        
        if self.group:
            self.args.append('self')
    
    def determine_name(self, value):
        self.name = acceptable(value)
        self.english = value
        different = self.english[1:-1] != self.name.replace('_', ' ')
        
        if self.typ == 'it':
            self.name = "test_%s" % self.name
        else:
            self.name = "ignore__%s" % self.name
        
        return different, self.name, self.english
    
    def add_arg(self, arg):
        self.args.append(arg)

class Group(object):
    def __init__(self, name=None, root=False, parent=None, level=0, typ=None, starting_group=False):
        self.kls = None
        self.typ = typ
        self.name = name
        self.root = root
        self.empty = True
        self.level = level
        self.parent = parent
        
        self.groups = []
        self.singles = []
        self.methods = []
        
        self.starting_group = starting_group
        self.starting_single = False
        
        if root:
            self.starting_group = False
    
    def __repr__(self):
        if self.at_root():
            return "<Root Group>"
        else:
            return "<Group %s:%s(%s)>" % (self.klsName, self.superKls, self.parent)
    
    @property
    def single(self):
        if self.singles:
            return self.singles[-1]
        
    @property
    def starting_signature(self):
        return self.starting_group or self.starting_single
    
    @property
    def klsName(self):
        # Determine kls for group
        if not self.parent or not self.parent.name:
            return 'Test{0}'.format(self.name)
        else:
            use = self.parent.klsName
            if use.startswith('Test'):
                use = use[4:]
            
            return 'Test{0}_{1}'.format(use, self.name)
    
    @property
    def superKls(self):
        if not self.kls and self.parent and self.parent.name:
            return self.parent.klsName
        return self.kls
        
    def at_root(self):
        return self.root
    
    def start_group(self, scol, typ):        
        new_group = Group(parent=self, level=scol, typ=typ, starting_group=True)
        self.groups.append(new_group)
        return new_group
    
    def start_single(self, typ, scol):
        group = None
        if not self.at_root():
            group = self
        
        new_single = Single(typ=typ, group=group, indent=(scol - self.level))
        self.singles.append(new_single)
        self.starting_single = True
        return new_single
    
    def name_single(self, name):
        different, name, english = self.single.determine_name(name)
        if different:
            identifier = name
            if not self.at_root():
                identifier = '%s.%s' % (self.klsName, name)
            self.methods.append((identifier, english))
    
    def finish_signature(self):
        self.starting_group = False
        self.starting_single = False
                
    def modify_kls(self, name):
        if self.kls is None:
            self.kls = name
        else:
            self.kls += name
    
    def determine_name(self, value):
        # Get english and python name for group
        self.name = acceptable(value, True)

class Tracker(object):
    def __init__(self, result, defaultKls='object'):
        if result is None:
            result = []
        self.result = result
        
        self.groups = Group(root=True)
        self.tokens = Tokens(defaultKls)
        self.single = self.groups.single
        
        self.allGroups = [self.groups]
        self.containers = []
        self.ignoreNext = []
        self.indentType = ' '
        self.afterSpace = True
        self.indentAmounts = []
        self.adjustIndentAt = []
        
        self.last = TokenDetails(value=' ')
        self._current = TokenDetails()
    
    @property
    def current(self):
        return self._current
    
    @current.setter
    def current(self, values):        
        self._current.transfer(self.last)
        self._current.set(*values)
    
    @contextmanager
    def add_phase(self):
        # add stuff
        yield self
        
        # Last thing may have beeen a skippable test
        self.finishHanging()

        # Remove trailing indents and dedents
        while len(self.result) > 1 and self.result[-2][0] in (INDENT, ERRORTOKEN, NEWLINE):
            self.result.pop(-2)
    
    def next_token(self, tokenum, value, scol):
        if self.current.tokenum == INDENT and self.current.value:
            self.indentType = self.current.value[0]
        
        self.current = (tokenum, value, scol)
        
        if not self.ignore_token():
            # Determining if this token is whitespace
            self.isWhitespace()
            
            # Determine if inside a container
            self.determineInsideContainer()
            
            # Change indentation as necessary
            self.determineIndentation()
            
            # Progress the tracker
            self.progress()
            
            if self.single and self.single.skipped:
                self.single.skipped = False
                self.result.append((NEWLINE, '\n'))
            
            # So next line knows if it is after space
            self.afterSpace = self.isSpace

    ########################
    ###   UTILITY
    ########################
        
    def addTokens(self, tokens):
        self.result.extend([d for d in tokens])
    
    def add_pass(self):
        # Make sure pass not added to group again
        self.groups.empty = False
        
        # Remove existing newline/indentation
        while self.result[-1][0] in (INDENT, NEWLINE):
            self.result.pop()
        
        # Add pass and indentation
        self.addTokens(
            [ (NAME, 'pass')
            , (NEWLINE, '\n')
            , (INDENT, self.indentType * self.current.scol)
            ]
        )
    
    def makeMethodNames(self):
        lst = []
        for group in self.allGroups:
            for cleaned, english in group.methods:
                lst.extend(self.tokens.makeNameModifier(not group.at_root(), cleaned, english))
        return lst
    
    def makeDescribeAttrs(self):
        lst = []
        if self.allGroups:
            lst.append((NEWLINE, '\n'))
            lst.append((INDENT, ''))

            for group in self.allGroups:
                if group.name:
                    lst.extend(self.tokens.makeDescribeAttr(group.klsName))
        
        return lst

    ########################
    ###   PROGRESS
    ########################
            
    def progress(self):
        # Determining what to replace and with what
        tokenum, value, scol = self.current.tokenum, self.current.value, self.current.scol
        
        # Default to not appending anything
        justAppend = False
        
        # Prevent from group having automatic pass given to it
        if tokenum == NAME and value == 'pass':
            self.groups.empty = False
        
        # Set variables to be used later on to determine if this will likely make group not empty
        createdGroup = False
        foundContent = False
        if not self.groups.starting_group and not self.isSpace:
            foundContent = True
        
        if self.groups.starting_group:
            # Inside a group signature, add to it
            if tokenum == NAME or (tokenum == OP and value == '.'):
                self.groups.modify_kls(value)

            elif tokenum == STRING:
                self.groups.determine_name(value)
            
            elif tokenum == NEWLINE:
                # Premature end of group
                self.add_group_tokens(with_pass=True)
            
            elif tokenum == OP and value == ":":
                # Proper end of group
                self.add_group_tokens()
        
        elif self.groups.starting_single:
            # Inside single signature, add to it
            if tokenum == STRING:
                self.groups.name_single(value)
            
            elif tokenum == NAME:
                self.single.add_arg(value)
            
            elif tokenum == NEWLINE:
                # Premature end of single
                self.add_single_tokens(ignore=True)
            
            elif tokenum == OP and value == ":":
                # Proper end of single
                self.add_single_tokens()
        
        elif self.afterSpace or scol == 0 and tokenum == NAME:
            if value in ('describe', 'context'):
                createdGroup = True
                
                # add pass to previous group if nothing added between then and now
                if self.groups.empty and not self.groups.at_root():
                    self.add_pass()
                
                # Start new group
                self.groups = self.groups.start_group(scol, value)
                self.allGroups.append(self.groups)
                
            elif value in ('it', 'ignore'):
                self.single = self.groups.start_single(value, scol)

            elif value in ('before_each', 'after_each'):
                self.add_test_helpers(value)
            
            else:
                justAppend = True
        else:
            # Don't care about it, append!
            justAppend = True
        
        # Found something that isn't whitespace or a new group
        # Hence current group isn't empty !
        if foundContent and not createdGroup:
            self.groups.empty = False
        
        # Just append if token should be
        if justAppend:
            # First ensure, the indentation has been normalised (incase of nesting)
            if tokenum == INDENT and not self.groups.at_root():
                value = value[self.groups.level:]
            
            self.result.append([tokenum, value])

    ########################
    ###   TRACK
    ########################
        
    def add_test_helpers(self, value):
        # Add tokens for this block
        tokens = getattr(self.tokens, value)
        self.result.extend(tokens)
        
        if not self.groups.at_root():
            # We need to adjust the indent before the super call later on
            self.adjustIndentAt.append(len(self.result) + 2)
            
            # Add super call if we have a super class
            self.result.extend(self.tokens.makeSuper(self.indentType * self.current.scol, self.groups.klsName, value))
            
            # Make sure colon and newline are ignored
            # Already added as part of making super
            expecting = [ (OP, ':')
                        , (NEWLINE, '\n')
                        ]
            
            self.ignoreNext = expecting
    
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
    
    def add_group_tokens(self, with_pass=False):
        kls = self.groups.superKls
        name = self.groups.klsName
        level = self.groups.level
        
        # Making sure this line starts at the beginning
        # By editing previous INDENT
        while self.result and self.result[-1][0] == INDENT:
            self.result.pop()
        
        self.result.append((INDENT, ''))
        self.result.extend(self.tokens.makeDescribe(kls, name))
        if with_pass:
            self.add_pass()
        
        self.groups.finish_signature()
    
    def add_single_tokens(self, ignore=False):
        name = self.single.name
        args = self.single.args
        
        # Remove any previous indent
        while self.result and self.result[-1][0] == INDENT:
            self.result.pop()
        
        # Make sure it starts with proper indent
        self.result.append((INDENT, self.indentType * self.single.indent))
        
        self.result.extend(self.tokens.makeSingle(name, args))
        if self.single.isIgnore or ignore:
            self.single.skipped = True
            self.result.extend(self.tokens.testSkip)
        
        self.groups.finish_signature()
    
    def determineInsideContainer(self):
        tokenum, value = self.current.tokenum, self.current.value
        self.endingContainer = False
        self.startingContainer = False
        
        if tokenum == OP:
            # Record when we're inside a container of some sort (tuple, list, dictionary)
            # So that we can care about that when determining what to do with whitespace
            if value in ['(', '[', '{']:
                # add to the stack because we started a list
                self.containers.append(value)
                self.startingContainer = True

            elif value in [')', ']', '}']:
                # not necessary to check for correctness
                self.containers.pop()
                self.endingContainer = True
        
    def determineIndentation(self):        
        # Ensuring NEWLINE tokens are actually specified as such
        if self.current.tokenum != NEWLINE and self.current.value == '\n':
            self.current.tokenum = NEWLINE
        
        # I want to change dedents into indents, because they seem to screw nesting up
        if self.current.tokenum == DEDENT:
            self.current.tokenum, self.current.value = self.convertDedent()
        
        if self.afterSpace and self.current.tokenum not in (NEWLINE, DEDENT, INDENT):
            if not self.containers:
                # We don't care about indentation inside a group (list, tuple or dictionary)
                # Record current indentation level
                if not self.indentAmounts or self.current.scol > self.indentAmounts[-1]:
                    self.indentAmounts.append(self.current.scol)

                while self.adjustIndentAt:
                    self.result[self.adjustIndentAt.pop()] = (INDENT, self.indentType * (self.current.scol - self.groups.level))
        
        # Roll back groups as necessary
        inContainer = len(self.containers) or (len(self.containers) == 1 and not self.startingContainer)
        endOfContainer = not len(self.containers) and self.endingContainer
        if not self.isSpace and not inContainer and not endOfContainer:
            while not self.groups.at_root() and self.groups.level >= self.current.scol:
                self.finishHanging()
                self.groups = self.groups.parent
    
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
        while self.result[-1][0] == INDENT:
            self.result.pop()
            
        value = self.indentType * lastIndent
        return tokenum, value
        
    def isWhitespace(self):
        tokenum, value = self.current.tokenum, self.current.value
        
        if value == '\n':
            self.isSpace = True
        else:
            self.isSpace = False
            if (value == '' or regexes['whitespace'].match(value)):
                self.isSpace = True
    
    def finishHanging(self):
        if self.groups.starting_signature:
            if self.groups.starting_group:
                self.add_group_tokens(with_pass=True)
            
            elif self.groups.starting_single:
                self.add_single_tokens(ignore=True)

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
