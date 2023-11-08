from tokenize import COMMENT, INDENT, NAME, NEWLINE, OP, STRING, generate_tokens

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

        self.single_colon = (OP, ":")

    ########################
    ###   MAKERS
    ########################

    def make_single(self, name, args, comments, return_type):
        if return_type is True:
            return_type = [(STRING, "->"), (NAME, "None")]
        elif return_type is None:
            return_type = []

        lst = [(NAME, "def"), (NAME, name), (OP, "(")] + [
            (t, n) for t, n, *_ in args if t is not None
        ]

        has_end = True
        has_pass = False

        if lst[-1][1] == ":":
            lst.pop()
        elif return_type and return_type[-1][1] == ":":
            return_type.pop()
        elif lst[-1][1] == "pass" and lst[-2][1] == ":":
            has_pass = True
            lst.pop()
            lst.pop()
        elif return_type and return_type[-1][1] == "pass" and return_type[-2][1] == ":":
            has_pass = True
            return_type.pop()
            return_type.pop()
        else:
            has_end = False

        if not has_end:
            srow = args[-1][-2]
            scol = args[-1][-1]
            raise SyntaxError(f"Found a missing ':' on line {srow}, column {scol}")

        lst.append((OP, ")"))
        lst.extend(return_type)
        lst.append((OP, ":"))

        if has_pass:
            lst.append((NAME, "pass"))

        lst.extend(comments)
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
            (COMMENT, " # type: ignore"),
        ]

    def make_name_modifier(self, cleaned, english):
        result = [(NEWLINE, "\n")]

        parts = cleaned.split(".")
        result.append((NAME, parts[0]))

        for part in parts[1:]:
            result.extend([(OP, "."), (NAME, part)])

        result.extend(
            [
                (OP, "."),
                (NAME, "__testname__"),
                (OP, "="),
                (STRING, english),
                (COMMENT, "  # type: ignore"),
            ]
        )

        return result
