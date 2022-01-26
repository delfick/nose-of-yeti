from tokenize import NAME, COMMENT
import re

regexes = {
    "joins": re.compile(r"[- /]"),
    "repeated_underscore": re.compile(r"_{2,}"),
    "invalid_variable_name_start": re.compile(r"^[^a-zA-Z_]"),
    "invalid_variable_name_characters": re.compile(r"[^0-9a-zA-Z_]"),
}


def acceptable(name, capitalize=False):
    """Convert a string into something that can be used as a valid python variable name"""
    # Convert space and dashes into underscores
    name = regexes["joins"].sub("_", name)

    # Remove invalid characters
    name = regexes["invalid_variable_name_characters"].sub("", name)

    # Remove leading characters until we find a letter or underscore
    name = regexes["invalid_variable_name_start"].sub("", name)

    # Clean up irregularities in underscores.
    name = regexes["repeated_underscore"].sub("_", name.strip("_"))

    if capitalize:
        # We don't use python's built in capitalize method here because it
        # turns all upper chars into lower chars if not at the start of
        # the string and we only want to change the first character.
        name_parts = []
        for word in name.split("_"):
            name_parts.append(word[0].upper())
            if len(word) > 1:
                name_parts.append(word[1:])
        name = "".join(name_parts)

    return name


class TokenDetails:
    """Container for current token"""

    def __init__(self, tokenum=None, value=None, srow=0, scol=0):
        self.set(tokenum, value, srow, scol)

    def set(self, tokenum, value, srow, scol):
        self.srow = srow
        self.scol = scol
        self.value = value
        self.tokenum = tokenum

    def transfer(self, details):
        details.set(*self.values())

    def values(self):
        return self.tokenum, self.value, self.srow, self.scol


class Single:
    """Container for a single block (i.e. it or ignore block)"""

    def __init__(self, srow, scol, group, typ=None, indent=0):
        self.typ = typ
        self.group = group
        self.indent = indent

        self.args = []
        self.comments = []

        self._name = None
        self.english = None
        self.skipped = False

        self.started_arg = False
        self.starting_arg = False

        if not self.group.root:
            self.args.append((NAME, "self", srow, scol))
        else:
            self.args.append((None, None, srow, scol))

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = acceptable(value)
        self.english = value

    @property
    def python_name(self):
        if self.typ == "it":
            return f"test_{self.name}"
        else:
            return f"ignore__{self.name}"

    @property
    def identifier(self):
        if self.group.root:
            return self.python_name
        else:
            return f"{self.group.kls_name}.{self.python_name}"

    def add_to_arg(self, tokenum, value, srow, scol):
        if value == "," and len(self.args) == 1 and self.args[0][0] is None:
            return

        if self.comments or tokenum is COMMENT:
            self.comments.append((tokenum, value))
        else:
            self.args.append((tokenum, value, srow, scol))


class Group:
    """Container for describe blocks"""

    def __init__(self, name=None, root=False, parent=None, level=0, typ=None):
        self.kls = None
        self.typ = typ
        self.name = name
        self.root = root
        self.empty = True
        self.level = level
        self.parent = parent
        self.singles = []
        self.has_after_each = False
        self.async_after_each = False
        self.has_before_each = False
        self.async_before_each = False

        # Default whether this group is starting anything
        self.starting_single = False
        if root:
            # Root technically isn't a group, so it doesn't have a signature to start
            self.starting_group = False
        else:
            # Group is created before we have all information
            # Hence it's signature is being created
            self.starting_group = True

    def __repr__(self):
        if self.root:
            return "<Root Group>"
        else:
            return f"<Group {self.kls_name}:{self.super_kls}({self.parent})>"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        self.english = value
        if value:
            self._name = acceptable(value, True)

    @property
    def starting_signature(self):
        """Determine if this group is starting itself or anything belonging to it"""
        return self.starting_group or self.starting_single

    @property
    def kls_name(self):
        """Determine python name for group"""
        # Determine kls for group
        if not self.parent or not self.parent.name:
            return f"Test{self.name}"
        else:
            use = self.parent.kls_name
            if use.startswith("Test"):
                use = use[4:]

            return f"Test{use}_{self.name}"

    @property
    def super_kls(self):
        """
        Determine what kls this group inherits from
        If default kls should be used, then None is returned
        """
        if not self.kls and self.parent and self.parent.name:
            return self.parent.kls_name
        return self.kls

    def start_group(self, scol, typ):
        """Start a new group"""
        return Group(parent=self, level=scol, typ=typ)

    def start_single(self, typ, srow, scol):
        """Start a new single"""
        self.starting_single = True
        single = self.single = Single(srow, scol, self, typ=typ, indent=(scol - self.level))
        self.singles.append(single)
        return single

    def finish_signature(self):
        """Tell group it isn't starting anything anymore"""
        self.starting_group = False
        self.starting_single = False

    def modify_kls(self, name):
        """Add a part to what will end up being the kls' superclass"""
        if self.kls is None:
            self.kls = name
        else:
            self.kls += name
