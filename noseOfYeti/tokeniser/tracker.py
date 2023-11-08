import re
from contextlib import contextmanager
from tokenize import (
    COMMENT,
    DEDENT,
    ENDMARKER,
    ERRORTOKEN,
    INDENT,
    NAME,
    NEWLINE,
    OP,
    STRING,
)

from noseOfYeti.tokeniser.containers import Group, TokenDetails

try:
    from tokenize import FSTRING_END, FSTRING_START
except ImportError:
    FSTRING_START, FSTRING_END = None, None

# Regex for matching whitespace
regexes = {"whitespace": re.compile(r"\s+")}


class WildCard:
    """Used to determine if tokens should be inserted until ignored token"""

    def __repr__(self):
        return "<WildCard>"


class Tracker:
    """Keep track of what each next token should mean"""

    def __init__(self, result, tokens, with_it_return_type=False):
        if result is None:
            self.result = []
        else:
            self.result = result

        self.with_it_return_type = with_it_return_type

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

        self.indent_type = " "
        self.insert_till = None
        self.after_space = True
        self.inserted_line = False
        self.after_an_async = False
        self.f_string_level = 0
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

    def next_token(self, tokenum, value, srow, scol):
        """Determine what to do with the next token"""

        # Make self.current reflect these values
        self.current.set(tokenum, value, srow, scol)

        # Determine indent_type based on this token
        if self.current.tokenum == INDENT and self.current.value:
            self.indent_type = self.current.value[0]

        # Only proceed if we shouldn't ignore this token
        if not self.ignore_token():
            # Determining the f string level
            self.determine_f_string_level()

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
                    self.result.append((OP, ";"))
                self.inserted_line = False

            # Progress the tracker
            self.progress()

            # Add a newline if we just skipped a single
            if self.single and self.single.skipped:
                self.single.skipped = False
                self.result.append((NEWLINE, "\n"))

            # Set after_space so next line knows if it is after space
            self.after_space = self.is_space

    def raise_about_open_containers(self):
        if self.containers:
            val, srow, scol = self.containers[-1]
            where = f"line {srow}, column {scol}"
            raise SyntaxError(f"Found an open '{val}' ({where}) that wasn't closed")

    ########################
    ###   PROGRESS
    ########################

    def progress(self):
        """
        Deal with next token
        Used to create, fillout and end groups and singles
        As well as just append everything else
        """
        tokenum, value, srow, scol = self.current.values()

        # Default to not appending anything
        just_append = False

        # Prevent from group having automatic pass given to it
        # If it already has a pass
        if tokenum == NAME and value == "pass":
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

            elif tokenum == NAME or (tokenum == OP and value == "."):
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
            if tokenum == STRING and not self.single.name:
                self.single.name = value
                self.single.args[0] = (
                    self.single.args[0][0],
                    self.single.args[0][1],
                    srow,
                    scol + len(value),
                )

            elif tokenum == NEWLINE and not self.in_container:
                self.add_tokens_for_single()
                self.result.append((tokenum, value))

            elif value and self.single.name:
                # Only want to add args after the name for the single has been specified
                self.single.add_to_arg(tokenum, value, srow, scol)

        elif self.after_space or self.after_an_async or scol == 0 and tokenum == NAME:
            # set after_an_async if we found an async by itself
            # So that we can just have that prepended and still be able to interpret our special blocks
            with_async = self.after_an_async
            if not self.after_an_async and value == "async":
                self.after_an_async = True
            else:
                self.after_an_async = False

            if value == "describe":
                created_group = True

                # add pass to previous group if nothing added between then and now
                if self.groups.empty and not self.groups.root:
                    self.add_tokens_for_pass()

                # Start new group
                self.groups = self.groups.start_group(scol, value)
                self.all_groups.append(self.groups)

            elif value in ("it", "ignore"):
                self.single = self.groups.start_single(value, srow, scol)

            elif value in ("before_each", "after_each"):
                setattr(self.groups, f"has_{value}", True)
                if with_async:
                    setattr(self.groups, f"async_{value}", True)
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
            # Make sure comments are indented appropriately
            add_dedent = False
            if tokenum == COMMENT and not self.in_container:
                indent = self.indent_type * (self.current.scol - self.groups.level)
                self.result.append((INDENT, indent))
                add_dedent = True

            self.result.append([tokenum, value])
            if add_dedent:
                self.result.append((DEDENT, ""))

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

                # Go through tokens until we find one that isn't a wildcard
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

    def make_method_names(self):
        """Create tokens for setting __testname__ on functions"""
        lst = [(NEWLINE, "\n"), (INDENT, "")]
        added = False

        for group in self.all_groups:
            for single in group.singles:
                name, english = single.name, single.english

                if english[1:-1] != name.replace("_", " "):
                    lst.extend(self.tokens.make_name_modifier(single.identifier, english))
                    added = True

        if not added:
            return

        endmarker = False

        if not all(l[0] == DEDENT for l in lst):
            if self.result and self.result[-1][0] is ENDMARKER:
                endmarker = True
                self.result.pop()
            self.result.extend(lst)

        if endmarker:
            self.result.append((ENDMARKER, ""))

    def make_describe_attrs(self):
        """Create tokens for setting is_noy_spec on describes"""
        if self.all_groups:
            self.result.append((NEWLINE, "\n"))
            self.result.append((INDENT, ""))

            for group in self.all_groups:
                if group.name:
                    self.result.extend(self.tokens.make_describe_attr(group.kls_name))

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
                append_at = -self.inserted_line + 1

            # Reset insert_till if we found it
            if (
                self.current.tokenum == self.insert_till[0]
                and self.current.value == self.insert_till[1]
            ):
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
            [(NAME, "pass"), (NEWLINE, "\n"), (INDENT, self.indent_type * self.current.scol)]
        )

    def add_tokens_for_test_helpers(self, value, with_async=False):
        """Add setup/teardown function to group"""
        # Add tokens for this block
        tokens = getattr(self.tokens, value)
        self.result.extend(tokens)

        # Add super call if we're inside a class
        if not self.groups.root:
            # We need to adjust the indent before the super call later on
            self.adjust_indent_at.append(len(self.result) + 2)

            # Add tokens for super call
            tokens_for_super = self.tokens.make_super(
                self.indent_type * self.current.scol,
                self.groups.kls_name,
                value,
                with_async=with_async,
            )
            self.result.extend(tokens_for_super)

            # Tell the machine we inserted a line
            self.inserted_line = len(tokens_for_super)

            # Make sure colon and newline are ignored
            # Already added as part of making super
            self.ignore_next = [(OP, ":"), WildCard(), (NEWLINE, "\n")]

    def add_tokens_for_group(self, with_pass=False):
        """Add the tokens for the group signature"""
        kls = self.groups.super_kls
        name = self.groups.kls_name

        # Reset indentation to beginning and add signature
        self.reset_indentation("")
        self.result.extend(self.tokens.make_describe(kls, name))

        # Add pass if necessary
        if with_pass:
            self.add_tokens_for_pass()

        self.groups.finish_signature()

    def add_tokens_for_single(self):
        """Add the tokens for the single signature"""
        args = self.single.args
        name = self.single.python_name
        comments = self.single.comments
        return_type = self.single.return_type
        if return_type is None and self.with_it_return_type:
            return_type = True

        # Reset indentation to proper amount
        if not self.result or self.result[-1][0] != NAME:
            self.reset_indentation(self.indent_type * self.single.indent)

        # And add signature
        self.result.extend(self.tokens.make_single(name, args, comments, return_type))
        self.groups.finish_signature()

    def finish_hanging(self):
        """Add tokens for hanging signature if any"""
        if self.groups.starting_signature:
            if self.groups.starting_group:
                self.add_tokens_for_group(with_pass=True)

            elif self.groups.starting_single:
                self.add_tokens_for_single()

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

        if value == "\n":
            self.is_space = True
        else:
            self.is_space = False
            if value == "" or regexes["whitespace"].match(value):
                if self.f_string_level == 0:
                    self.is_space = True

    def determine_f_string_level(self):
        """
        Set self.f_string_level depending on FSTRING_{START,END}
        """
        if self.current.tokenum == FSTRING_START:
            self.f_string_level += 1

        if self.current.tokenum == FSTRING_END:
            if self.f_string_level > 0:
                self.f_string_level -= 1

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
            srow = self.current.srow
            scol = self.current.scol

            # Record when we're inside a container of some sort (tuple, list, dictionary)
            # So that we can care about that when determining what to do with whitespace
            if value in ["(", "[", "{"]:
                # add to the stack because we started a list
                self.containers.append((value, srow, scol))
                starting_container = True

            elif value in [")", "]", "}"]:
                # not necessary to check for correctness
                if not self.containers:
                    raise SyntaxError(f"Found a hanging '{value}' on line {srow}, column {scol}")

                v, sr, sc = self.containers.pop()
                if v != {")": "(", "]": "[", "}": "{"}[value]:
                    found_at = f"line {srow}, column {scol}"
                    found_last = f"line {sr}, column {sc}"
                    msg = "Trying to close the wrong type of bracket"
                    msg = f"{msg}. Found '{value}' ({found_at}) instead of closing a '{v}' ({found_last})"
                    raise SyntaxError(msg)

                ending_container = True

        self.just_ended_container = not len(self.containers) and ending_container
        self.just_started_container = len(self.containers) == 1 and starting_container
        self.in_container = (
            len(self.containers) or self.just_ended_container or self.just_started_container
        )

    def determine_indentation(self):
        """Reset indentation for current token and in self.result to be consistent and normalized"""
        # Ensuring NEWLINE tokens are actually specified as such
        if self.current.tokenum != NEWLINE and self.current.value == "\n":
            self.current.tokenum = NEWLINE

        # I want to change dedents into indents, because they seem to screw nesting up
        if self.current.tokenum == DEDENT:
            self.current.tokenum, self.current.value = self.convert_dedent()

        if (
            self.after_space
            and not self.is_space
            and (not self.in_container or self.just_started_container)
        ):
            # Record current indentation level
            if not self.indent_amounts or self.current.scol > self.indent_amounts[-1]:
                self.indent_amounts.append(self.current.scol)

            # Adjust indent as necessary
            while self.adjust_indent_at:
                self.result[self.adjust_indent_at.pop()] = (
                    INDENT,
                    self.indent_type * (self.current.scol - self.groups.level),
                )

        # Roll back groups as necessary
        if not self.is_space and not self.in_container:
            while not self.groups.root and self.groups.level >= self.current.scol:
                self.finish_hanging()
                self.groups = self.groups.parent

        # Reset indentation to deal with nesting
        if self.current.tokenum == INDENT and not self.groups.root:
            self.current.value = self.current.value[self.groups.level :]

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
