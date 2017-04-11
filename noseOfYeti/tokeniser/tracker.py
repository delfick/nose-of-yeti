from tokenize import NAME, OP, INDENT, NEWLINE, DEDENT, STRING, ERRORTOKEN, COMMENT
from contextlib import contextmanager
import re

from noseOfYeti.tokeniser.containers import TokenDetails, Group

# Regex for matching whitespace
regexes = {'whitespace': re.compile('\s+')}

class WildCard(object):
    """Used to determine if tokens should be inserted untill ignored token"""
    def __repr__(self):
        return "<WildCard>"

class Tracker(object):
    """Keep track of what each next token should mean"""
    def __init__(self, result, tokens, wrapped_setup):
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
        self.wrapped_setup = wrapped_setup

        self.containers = []
        self.ignore_next = []
        self.indent_amounts = []
        self.adjust_indent_at = []

        self.indent_type = ' '
        self.insert_till = None
        self.after_space = True
        self.inserted_line = False
        self.after_an_async = False
        self.just_ended_container = False
        self.just_started_container = False

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

            # See if we are force inserting this token
            if self.forced_insert():
                return

            # If we have a newline after an inserted line, then we don't need to worry about semicolons
            if self.inserted_line and self.current.tokenum == NEWLINE:
                self.inserted_line = False

            # If we have a non space, non comment after an inserted line, then insert a semicolon
            if self.result and not self.is_space and self.inserted_line:
                if self.current.tokenum != COMMENT:
                    self.result.append((OP, ';'))
                self.inserted_line = False

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

        elif self.after_space or self.after_an_async or scol == 0 and tokenum == NAME:
            # set after_an_async if we found an async by itself
            # So that we can just have that prepended and still be able to interpret our special blocks
            with_async = self.after_an_async
            if not self.after_an_async and value == "async":
                self.after_an_async = True
            else:
                self.after_an_async = False

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
                setattr(self.groups, "has_%s" % value, True)
                if with_async:
                    setattr(self.groups, "async_%s" % value, True)
                self.add_tokens_for_test_helpers(value, with_async=with_async)

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
        def get_next_ignore(remove=False):
            """Get next ignore from ignore_next and remove from ignore_next"""
            next_ignore = self.ignore_next

            # Just want to return it, don't want to remove yet
            if not remove:
                if type(self.ignore_next) in (list, tuple):
                    next_ignore = self.ignore_next[0]
                return next_ignore

            # Want to remove it from ignore_next
            if type(next_ignore) in (list, tuple) and next_ignore:
                next_ignore = self.ignore_next.pop(0)
            elif not next_ignore:
                self.next_ignore = None
                next_ignore = None
            else:
                self.next_ignore = None

            return next_ignore

        # If we have tokens to be ignored and we're not just inserting till some token
        if not self.insert_till and self.ignore_next:
            # Determine what the next ignore is
            next_ignore = get_next_ignore()
            if next_ignore == (self.current.tokenum, self.current.value):
                # Found the next ignore token, remove it from the stack
                # So that the next ignorable token can be considered
                get_next_ignore(remove=True)
                return True
            else:
                # If not a wildcard, then return now
                if type(next_ignore) is not WildCard:
                    return False

                # Go through tokens untill we find one that isn't a wildcard
                while type(next_ignore) == WildCard:
                    next_ignore = get_next_ignore(remove=True)

                # If the next token is next ignore then we're done here!
                if next_ignore == (self.current.tokenum, self.current.value):
                    get_next_ignore(remove=True)
                    return True
                else:
                    # If there is another token to ignore, then consider the wildcard
                    # And keep inserting till we reach this next ignorable token
                    if next_ignore:
                        self.insert_till = next_ignore
                    return False

    def wrapped_setups(self):
        """Create tokens for Described.setup = noy_wrap_setup(Described, Described.setup) for setup/teardown"""
        lst = []
        for group in self.all_groups:
            if not group.root:
                if group.has_after_each:
                    lst.extend(self.tokens.wrap_after_each(group.kls_name, group.async_after_each))

                if group.has_before_each:
                    lst.extend(self.tokens.wrap_before_each(group.kls_name, group.async_before_each))

        if lst:
            indentation_reset = [
                  (NEWLINE, '\n')
                , (INDENT, '')
                ]
            lst = indentation_reset + lst

        return lst

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

    def forced_insert(self):
        """
            Insert tokens if self.insert_till hasn't been reached yet
            Will respect self.inserted_line and make sure token is inserted before it
            Returns True if it appends anything or if it reached the insert_till token
        """
        # If we have any tokens we are waiting for
        if self.insert_till:
            # Determine where to append this token
            append_at = -1
            if self.inserted_line:
                append_at = -self.inserted_line+1

            # Reset insert_till if we found it
            if self.current.tokenum == self.insert_till[0] and self.current.value == self.insert_till[1]:
                self.insert_till = None
            else:
                # Adjust self.adjust_indent_at to take into account the new token
                for index, value in enumerate(self.adjust_indent_at):
                    if value < len(self.result) - append_at:
                        self.adjust_indent_at[index] = value + 1

                # Insert the new token
                self.result.insert(append_at, (self.current.tokenum, self.current.value))

            # We appended the token
            return True

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

    def add_tokens_for_test_helpers(self, value, with_async=False):
        """Add setup/teardown function to group"""
        # Add tokens for this block
        tokens = getattr(self.tokens, value)
        self.result.extend(tokens)

        # Add super call if we're inside a class
        if not self.groups.root and not self.wrapped_setup:
            # We need to adjust the indent before the super call later on
            self.adjust_indent_at.append(len(self.result) + 2)

            # Add tokens for super call
            tokens_for_super = self.tokens.make_super(self.indent_type * self.current.scol, self.groups.kls_name, value, with_async=with_async)
            self.result.extend(tokens_for_super)

            # Tell the machine we inserted a line
            self.inserted_line = len(tokens_for_super)

            # Make sure colon and newline are ignored
            # Already added as part of making super
            self.ignore_next = [(OP, ':'), WildCard(), (NEWLINE, '\n')]

    def add_tokens_for_group(self, with_pass=False):
        """Add the tokens for the group signature"""
        kls = self.groups.super_kls
        name = self.groups.kls_name

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
        if ignore:
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

        self.just_ended_container = not len(self.containers) and ending_container
        self.just_started_container = len(self.containers) == 1 and starting_container
        self.in_container = len(self.containers) or self.just_ended_container or self.just_started_container

    def determine_indentation(self):
        """Reset indentation for current token and in self.result to be consistent and normalized"""
        # Ensuring NEWLINE tokens are actually specified as such
        if self.current.tokenum != NEWLINE and self.current.value == '\n':
            self.current.tokenum = NEWLINE

        # I want to change dedents into indents, because they seem to screw nesting up
        if self.current.tokenum == DEDENT:
            self.current.tokenum, self.current.value = self.convert_dedent()

        if self.after_space and not self.is_space and (not self.in_container or self.just_started_container):
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

