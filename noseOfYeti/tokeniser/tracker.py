from tokenize import NAME, OP, INDENT, NEWLINE, DEDENT, STRING, ERRORTOKEN
from contextlib import contextmanager
import re

from containers import TokenDetails, Single, Group

# Regex for matching whitespace
regexes = {'whitespace': re.compile('\s+')}

class Tracker(object):
    """Keep track of what each next token should mean"""
    def __init__(self, result, tokens):
        if result is None:
            self.result = []
        else:
            self.result = result
        
        self.single = None
        self.tokens = tokens
        self.groups = Group(root=True)
        self.current = TokenDetails()
        self.all_groups = [self.groups]
        self.in_container = False
        
        self.containers = []
        self.ignore_next = []
        self.indent_amounts = []
        self.adjust_indent_at = []
        
        self.indent_type = ' '
        self.after_space = True
    
    @contextmanager
    def add_phase(self):
        """Context manager for when adding all the tokens"""
        # add stuff
        yield self
        
        # Make sure we output eveything
        self.finish_hanging()
        
        # Remove trailing indents and dedents
        while len(self.result) > 1 and self.result[-2][0] in (INDENT, ERRORTOKEN, NEWLINE):
            self.result.pop(-2)
    
    def next_token(self, tokenum, value, scol):
        """Determine what to do with the next token"""
        
        # Make self.current reflect these values
        self.current.set(tokenum, value, scol)
        
        # Determine indent_type based on this token
        if self.current.tokenum == INDENT and self.current.value:
            self.indent_type = self.current.value[0]
        
        # Only proceed if we shouldn't ignore this token
        if not self.ignore_token():
            # Determining if this token is whitespace
            self.determine_if_whitespace()
            
            # Determine if inside a container
            self.determine_inside_container()
            
            # Change indentation as necessary
            self.determine_indentation()
            
            # Progress the tracker
            self.progress()
            
            # Add a newline if we just skipped a single
            if self.single and self.single.skipped:
                self.single.skipped = False
                self.result.append((NEWLINE, '\n'))
            
            # Set after_space so next line knows if it is after space
            self.after_space = self.is_space
    
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
        just_append = False
        
        # Prevent from group having automatic pass given to it
        # If it already has a pass
        if tokenum == NAME and value == 'pass':
            self.groups.empty = False
        
        # Set variables to be used later on to determine if this will likely make group not empty
        created_group = False
        found_content = False
        if not self.groups.starting_group and not self.is_space:
            found_content = True
        
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
            
            elif tokenum == NEWLINE and not self.in_container:
                # Premature end of single
                self.add_tokens_for_single(ignore=True)
            
            elif tokenum == OP and value == ":":
                # Proper end of single
                self.add_tokens_for_single()
            
            elif value and self.single.name:
                # Only want to add args after the name for the single has been specified
                self.single.add_to_arg(tokenum, value)
        
        elif self.after_space or scol == 0 and tokenum == NAME:
            if value in ('describe', 'context'):
                created_group = True
                
                # add pass to previous group if nothing added between then and now
                if self.groups.empty and not self.groups.root:
                    self.add_tokens_for_pass()
                
                # Start new group
                self.groups = self.groups.start_group(scol, value)
                self.all_groups.append(self.groups)
                
            elif value in ('it', 'ignore'):
                self.single = self.groups.start_single(value, scol)
            
            elif value in ('before_each', 'after_each'):
                self.add_tokens_for_test_helpers(value)
            
            else:
                just_append = True
        else:
            # Don't care about it, append!
            just_append = True
        
        # Found something that isn't whitespace or a new group
        # Hence current group isn't empty !
        if found_content and not created_group:
            self.groups.empty = False
        
        # Just append if token should be
        if just_append:
            self.result.append([tokenum, value])
    
    ########################
    ###   UTILITY
    ########################
        
    def add_tokens(self, tokens):
        """Add tokens to result"""
        self.result.extend([d for d in tokens])
    
    def reset_indentation(self, amount):
        """Replace previous indentation with desired amount"""
        while self.result and self.result[-1][0] == INDENT:
            self.result.pop()
        self.result.append((INDENT, amount))
    
    def ignore_token(self):
        """Determine if we should ignore current token"""
        if self.ignore_next:
            next_ignore = self.ignore_next
            if type(next_ignore) in (list, tuple):
                next_ignore = self.ignore_next.pop(0)
            
            if next_ignore == (self.current.tokenum, self.current.value):
                return True
            else:
                self.next_ignore = None
                return False
    
    def make_method_names(self):
        """Create tokens for setting __testname__ on functions"""
        lst = []
        for group in self.all_groups:
            for single in group.singles:
                name, english = single.name, single.english
                if english[1:-1] != name.replace('_', ' '):
                    lst.extend(self.tokens.make_name_modifier(not group.root, single.identifier, english))
        return lst
    
    def make_describe_attrs(self):
        """Create tokens for setting is_noy_spec on describes"""
        lst = []
        if self.all_groups:
            lst.append((NEWLINE, '\n'))
            lst.append((INDENT, ''))
            
            for group in self.all_groups:
                if group.name:
                    lst.extend(self.tokens.make_describe_attr(group.kls_name))
        
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
        self.add_tokens(
            [ (NAME, 'pass')
            , (NEWLINE, '\n')
            , (INDENT, self.indent_type * self.current.scol)
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
            self.adjust_indent_at.append(len(self.result) + 2)
            
            # Add tokens for super call
            self.result.extend(self.tokens.make_super(self.indent_type * self.current.scol, self.groups.kls_name, value))
            
            # Make sure colon and newline are ignored
            # Already added as part of making super
            self.ignore_next = [
                  (OP, ':')
                , (NEWLINE, '\n')
                ]
    
    def add_tokens_for_group(self, with_pass=False):
        """Add the tokens for the group signature"""
        kls = self.groups.super_kls
        name = self.groups.kls_name
        level = self.groups.level
        
        # Reset indentation to beginning and add signature
        self.reset_indentation('')
        self.result.extend(self.tokens.make_describe(kls, name))
        
        # Add pass if necessary
        if with_pass:
            self.add_tokens_for_pass()
        
        self.groups.finish_signature()
    
    def add_tokens_for_single(self, ignore=False):
        """Add the tokens for the single signature"""
        args = self.single.args
        name = self.single.python_name
        
        # Reset indentation to proper amount and add signature
        self.reset_indentation(self.indent_type * self.single.indent)
        self.result.extend(self.tokens.make_single(name, args))
        
        # Add skip if necessary
        if self.single.typ == 'ignore' or ignore:
            self.single.skipped = True
            self.result.extend(self.tokens.test_skip)
        
        self.groups.finish_signature()
    
    def finish_hanging(self):
        """Add tokens for hanging singature if any"""
        if self.groups.starting_signature:
            if self.groups.starting_group:
                self.add_tokens_for_group(with_pass=True)
            
            elif self.groups.starting_single:
                self.add_tokens_for_single(ignore=True)
    
    ########################
    ###   DETERMINE INFORMATION
    ########################
    
    def determine_if_whitespace(self):
        """
            Set is_space if current token is whitespace
            Is space if value is:
             * Newline
             * Empty String
             * Something that matches regexes['whitespace']
        """
        value = self.current.value
        
        if value == '\n':
            self.is_space = True
        else:
            self.is_space = False
            if (value == '' or regexes['whitespace'].match(value)):
                self.is_space = True
    
    def determine_inside_container(self):
        """
            Set self.in_container if we're inside a container
             * Inside container
             * Current token starts a new container
             * Current token ends all containers
        """
        tokenum, value = self.current.tokenum, self.current.value
        ending_container = False
        starting_container = False
        
        if tokenum == OP:
            # Record when we're inside a container of some sort (tuple, list, dictionary)
            # So that we can care about that when determining what to do with whitespace
            if value in ['(', '[', '{']:
                # add to the stack because we started a list
                self.containers.append(value)
                starting_container = True
            
            elif value in [')', ']', '}']:
                # not necessary to check for correctness
                self.containers.pop()
                ending_container = True
        
        just_ended = not len(self.containers) and ending_container
        just_started = len(self.containers) == 1 and not starting_container
        self.in_container = len(self.containers) or just_started or just_ended
    
    def determine_indentation(self):
        """Reset indentation for current token and in self.result to be consistent and normalized"""
        # Ensuring NEWLINE tokens are actually specified as such
        if self.current.tokenum != NEWLINE and self.current.value == '\n':
            self.current.tokenum = NEWLINE
        
        # I want to change dedents into indents, because they seem to screw nesting up
        if self.current.tokenum == DEDENT:
            self.current.tokenum, self.current.value = self.convert_dedent()
        
        if not self.in_container and self.after_space and self.current.tokenum not in (NEWLINE, DEDENT, INDENT):
            # Record current indentation level
            if not self.indent_amounts or self.current.scol > self.indent_amounts[-1]:
                self.indent_amounts.append(self.current.scol)
            
            # Adjust indent as necessary
            while self.adjust_indent_at:
                self.result[self.adjust_indent_at.pop()] = (INDENT, self.indent_type * (self.current.scol - self.groups.level))
        
        # Roll back groups as necessary
        if not self.is_space and not self.in_container:
            while not self.groups.root and self.groups.level >= self.current.scol:
                self.finish_hanging()
                self.groups = self.groups.parent
        
        # Reset indentation to deal with nesting
        if self.current.tokenum == INDENT and not self.groups.root:
           self.current.value = self.current.value[self.groups.level:]
    
    def convert_dedent(self):
        """Convert a dedent into an indent"""
        # Dedent means go back to last indentation
        if self.indent_amounts:
            self.indent_amounts.pop()
        
        # Change the token
        tokenum = INDENT
        
        # Get last indent amount
        last_indent = 0
        if self.indent_amounts:
            last_indent = self.indent_amounts[-1]
        
        # Make sure we don't have multiple indents in a row
        while self.result[-1][0] == INDENT:
            self.result.pop()
            
        value = self.indent_type * last_indent
        return tokenum, value