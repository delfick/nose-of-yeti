from tokenize import NAME, OP, INDENT, NEWLINE, STRING
from tokenize import generate_tokens

########################
###   TOKENS IN GENERATOR
########################


def tokens_in(s, strip_it=True):
    closure = {"processed": False}

    def get():
        if closure["processed"]:
            return ""

        closure["processed"] = True
        if strip_it:
            return s.strip()
        else:
            return s

    res = [(t, v) for t, v, _, _, _ in generate_tokens(get)][:-1]
    while res and res[-1][0] == 4:
        res.pop()
    return res


########################
###   TOKENS
########################


class Tokens:
    def __init__(self):
        self.equivalence = {"after_each": "tearDown", "before_each": "setUp"}

        self.before_each = [
            (NAME, "def"),
            (NAME, self.equivalence["before_each"]),
            (OP, "("),
            (NAME, "self"),
            (OP, ")"),
        ]

        self.after_each = [
            (NAME, "def"),
            (NAME, self.equivalence["after_each"]),
            (OP, "("),
            (NAME, "self"),
            (OP, ")"),
        ]

    ########################
    ###   MAKERS
    ########################

    def make_single(self, name, args):
        lst = [(NAME, "def"), (NAME, name), (OP, "(")]

        if args:
            lst.extend(args[0])

            for arg in args[1:]:
                lst.append((OP, ","))
                lst.extend(arg)

        lst.extend([(OP, ")"), (OP, ":")])
        return lst

    def make_describe(self, kls, name):
        lst = [(NAME, "class"), (NAME, name)]
        if kls:
            lst.append((OP, "("))
            lst.extend(tokens_in(kls))
            lst.append((OP, ")"))

        lst.append((OP, ":"))

        return lst

    def make_super(self, indent, kls, method, with_async=False):
        if kls:
            kls = tokens_in(kls)

        prefix = "async" if with_async else "sync"

        result = [(OP, ":"), (NEWLINE, "\n"), (INDENT, indent)]

        if with_async:
            result.append((NAME, "await"))

        result.extend(
            [
                (NAME, "__import__"),
                (OP, "("),
                (OP, '"'),
                (STRING, "noseOfYeti"),
                (OP, '"'),
                (OP, ")"),
                (OP, "."),
                (NAME, "tokeniser"),
                (OP, "."),
                (NAME, "TestSetup"),
                (OP, "("),
                (NAME, "super"),
                (OP, "("),
                (OP, ")"),
                (OP, ")"),
                (OP, "."),
                (NAME, f"{prefix}_{method}"),
                (OP, "("),
                (OP, ")"),
            ]
        )

        return result

    def make_describe_attr(self, describe):
        return [
            (NEWLINE, "\n"),
            (NAME, describe),
            (OP, "."),
            (NAME, "is_noy_spec"),
            (OP, "="),
            (NAME, "True"),
        ]

    def make_name_modifier(self, cleaned, english):
        result = [(NEWLINE, "\n")]

        parts = cleaned.split(".")
        result.append((NAME, parts[0]))

        for part in parts[1:]:
            result.extend([(OP, "."), (NAME, part)])

        result.extend([(OP, "."), (NAME, "__testname__"), (OP, "="), (STRING, english)])

        return result
