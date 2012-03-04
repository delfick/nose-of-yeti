from tokenize import NAME, OP, INDENT, NEWLINE, DEDENT, STRING, ERRORTOKEN
from contextlib import contextmanager
from tokens import Tokens, tokensIn
import re

from containers import TokenDetails, Single, Group

# Regex for matching whitespace
regexes = {'whitespace': re.compile('\s+')}

class Tracker(object):
    """Keep track of what each next token should mean"""
    def __init__(self, result, defaultKls='object'):
        self.result = result or []
        
        self.single = None
        self.groups = Group(root=True)
        self.tokens = Tokens(defaultKls)
        self.current = TokenDetails()
        self.allGroups = [self.groups]
        
        self.containers = []
        self.ignoreNext = []
        self.indentAmounts = []
        self.adjustIndentAt = []
        
        self.indentType = ' '
        self.afterSpace = True
    
    @contextmanager
    def add_phase(self):
        """Context manager for when adding all the tokens"""
        # add stuff
        yield self
        
        # Make sure we output eveything
        self.finishHanging()

        # Remove trailing indents and dedents
        while len(self.result) > 1 and self.result[-2][0] in (INDENT, ERRORTOKEN, NEWLINE):
            self.result.pop(-2)
    
    def next_token(self, tokenum, value, scol):
        """Determine what to do with the next token"""
        
        # Make self.current reflect these values
        self.current.set(tokenum, value, scol)
        
        # Determine indentType based on this token
        if self.current.tokenum == INDENT and self.current.value:
            self.indentType = self.current.value[0]
        
        # Only proceed if we shouldn't ignore this token
        if not self.ignore_token():
            # Determining if this token is whitespace
            self.determineIfWhitespace()
            
            # Determine if inside a container
            self.determineInsideContainer()
            
            # Change indentation as necessary
            self.determineIndentation()
            
            # Progress the tracker
            self.progress()
            
            # Add a newline if we just skipped a single
            if self.single and self.single.skipped:
                self.single.skipped = False
                self.result.append((NEWLINE, '\n'))
            
            # Set afterSpace so next line knows if it is after space
            self.afterSpace = self.isSpace

    ########################
    ###   PROGRESS
    ########################
            
    def progress(self):
        """
            Deal with next token
            Used to create, fillout and end groups and singles
            As well as just append everything else
        """
        tokenum, value, scol = self.current.values()
        
        # Default to not appending anything
        justAppend = False
        
        # Prevent from group having automatic pass given to it
        # If it already has a pass
        if tokenum == NAME and value == 'pass':
            self.groups.empty = False
        
        # Set variables to be used later on to determine if this will likely make group not empty
        createdGroup = False
        foundContent = False
        if not self.groups.starting_group and not self.isSpace:
            foundContent = True
        
        if self.groups.starting_group:
            # Inside a group signature, add to it
            if tokenum == STRING:
                self.groups.name = value
            
            elif tokenum == NAME or (tokenum == OP and value == '.'):
                # Modify super class for group
                self.groups.modify_kls(value)
            
            elif tokenum == NEWLINE:
                # Premature end of group
                self.add_tokens_for_group(with_pass=True)
            
            elif tokenum == OP and value == ":":
                # Proper end of group
                self.add_tokens_for_group()
        
        elif self.groups.starting_single:
            # Inside single signature, add to it
            if tokenum == STRING:
                self.single.name = value
            
            elif tokenum == NAME:
                self.single.add_arg(value)
            
            elif tokenum == NEWLINE:
                # Premature end of single
                self.add_tokens_for_single(ignore=True)
            
            elif tokenum == OP and value == ":":
                # Proper end of single
                self.add_tokens_for_single()
        
        elif self.afterSpace or scol == 0 and tokenum == NAME:
            if value in ('describe', 'context'):
                createdGroup = True
                
                # add pass to previous group if nothing added between then and now
                if self.groups.empty and not self.groups.root:
                    self.add_tokens_for_pass()
                
                # Start new group
                self.groups = self.groups.start_group(scol, value)
                self.allGroups.append(self.groups)
                
            elif value in ('it', 'ignore'):
                self.single = self.groups.start_single(value, scol)

            elif value in ('before_each', 'after_each'):
                self.add_tokens_for_test_helpers(value)
            
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
            self.result.append([tokenum, value])

    ########################
    ###   UTILITY
    ########################
        
    def addTokens(self, tokens):
        """Add tokens to result"""
        self.result.extend([d for d in tokens])
    
    def resetIndentation(self, amount):
        """Replace previous indentation with desired amount"""
        while self.result and self.result[-1][0] == INDENT:
            self.result.pop()
        self.result.append((INDENT, amount))
    
    def ignore_token(self):
        """Determine if we should ignore current token"""
        if self.ignoreNext:
            nextIgnore = self.ignoreNext
            if type(nextIgnore) in (list, tuple):
                nextIgnore = self.ignoreNext.pop(0)
            
            if nextIgnore == (self.current.tokenum, self.current.value):
                return True
            else:
                self.nextIgnore = None
                return False
    
    def makeMethodNames(self):
        """Create tokens for setting __testname__ on functions"""
        lst = []
        for group in self.allGroups:
            for single in group.singles:
                name, english = single.name, single.english
                if english[1:-1] != name.replace('_', ' '):
                    lst.extend(self.tokens.makeNameModifier(not group.root, single.identifier, english))
        return lst
    
    def makeDescribeAttrs(self):
        """Create tokens for setting is_noy_spec on describes"""
        lst = []
        if self.allGroups:
            lst.append((NEWLINE, '\n'))
            lst.append((INDENT, ''))

            for group in self.allGroups:
                if group.name:
                    lst.extend(self.tokens.makeDescribeAttr(group.klsName))
        
        return lst

    ########################
    ###   ADD TOKENS
    ########################
    
    def add_tokens_for_pass(self):
        """Add tokens for a pass to result"""
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
        
    def add_tokens_for_test_helpers(self, value):
        """Add setup/teardown function to group"""
        # Add tokens for this block
        tokens = getattr(self.tokens, value)
        self.result.extend(tokens)
        
        # Add super call if we're inside a class
        if not self.groups.root:
            # We need to adjust the indent before the super call later on
            self.adjustIndentAt.append(len(self.result) + 2)
            
            # Add tokens for super call
            self.result.extend(self.tokens.makeSuper(self.indentType * self.current.scol, self.groups.klsName, value))
            
            # Make sure colon and newline are ignored
            # Already added as part of making super
            self.ignoreNext = [ 
                  (OP, ':')
                , (NEWLINE, '\n')
                ]
    
    def add_tokens_for_group(self, with_pass=False):
        """Add the tokens for the group signature"""
        kls = self.groups.superKls
        name = self.groups.klsName
        level = self.groups.level
        
        # Reset indentation to beginning and add signature
        self.resetIndentation('')
        self.result.extend(self.tokens.makeDescribe(kls, name))
        
        # Add pass if necessary
        if with_pass:
            self.add_tokens_for_pass()
        
        self.groups.finish_signature()
    
    def add_tokens_for_single(self, ignore=False):
        """Add the tokens for the single signature"""
        args = self.single.args
        name = self.single.python_name
        
        # Reset indentation to proper amount and add signature
        self.resetIndentation(self.indentType * self.single.indent)
        self.result.extend(self.tokens.makeSingle(name, args))
        
        # Add skip if necessary
        if self.single.typ == 'ignore' or ignore:
            self.single.skipped = True
            self.result.extend(self.tokens.testSkip)
        
        self.groups.finish_signature()
    
    def finishHanging(self):
        """Add tokens for hanging singature if any"""
        if self.groups.starting_signature:
            if self.groups.starting_group:
                self.add_tokens_for_group(with_pass=True)
            
            elif self.groups.starting_single:
                self.add_tokens_for_single(ignore=True)

    ########################
    ###   DETERMINE INFORMATION
    ########################
        
    def determineIfWhitespace(self):
        """
            Set isSpace if current token is whitespace
            Is space if value is:
             * Newline
             * Empty String
             * Something that matches regexes['whitespace']
        """
        value = self.current.value
        
        if value == '\n':
            self.isSpace = True
        else:
            self.isSpace = False
            if (value == '' or regexes['whitespace'].match(value)):
                self.isSpace = True
    
    def determineInsideContainer(self):
        """
            Set self.inContainer if we're inside a container
             * Inside container
             * Current token starts a new container
             * Current token ends all containers
        """
        tokenum, value = self.current.tokenum, self.current.value
        endingContainer = False
        startingContainer = False
        
        if tokenum == OP:
            # Record when we're inside a container of some sort (tuple, list, dictionary)
            # So that we can care about that when determining what to do with whitespace
            if value in ['(', '[', '{']:
                # add to the stack because we started a list
                self.containers.append(value)
                startingContainer = True

            elif value in [')', ']', '}']:
                # not necessary to check for correctness
                self.containers.pop()
                endingContainer = True
        
        just_ended = not len(self.containers) and endingContainer
        just_started = len(self.containers) == 1 and not startingContainer
        self.inContainer = len(self.containers) or just_started or just_ended
        
    def determineIndentation(self):
        """Reset indentation for current token and in self.result to be consistent and normalized"""      
        # Ensuring NEWLINE tokens are actually specified as such
        if self.current.tokenum != NEWLINE and self.current.value == '\n':
            self.current.tokenum = NEWLINE
        
        # I want to change dedents into indents, because they seem to screw nesting up
        if self.current.tokenum == DEDENT:
            self.current.tokenum, self.current.value = self.convertDedent()
        
        if not self.inContainer and self.afterSpace and self.current.tokenum not in (NEWLINE, DEDENT, INDENT):
            # Record current indentation level
            if not self.indentAmounts or self.current.scol > self.indentAmounts[-1]:
                self.indentAmounts.append(self.current.scol)
            
            # Adjust indent as necessary
            while self.adjustIndentAt:
                self.result[self.adjustIndentAt.pop()] = (INDENT, self.indentType * (self.current.scol - self.groups.level))
        
        # Roll back groups as necessary
        if not self.isSpace and not self.inContainer:
            while not self.groups.root and self.groups.level >= self.current.scol:
                self.finishHanging()
                self.groups = self.groups.parent
        
        # Reset indentation to deal with nesting
        if self.current.tokenum == INDENT and not self.groups.root:
           self.current.value = self.current.value[self.groups.level:]
    
    def convertDedent(self):
        """Convert a dedent into an indent"""
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