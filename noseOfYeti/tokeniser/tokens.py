from tokenize import NAME, OP, INDENT, NEWLINE, STRING
from tokenize import generate_tokens

import six

########################
###   TOKENS IN GENERATOR
########################

def tokens_in(s, strip_it=True):
    closure = {'processed': False}
    def get():
        if closure['processed']:
            return ''

        closure['processed'] = True
        if strip_it:
            return s.strip()
        else:
            return s
    return [(t, v) for t, v, _, _, _ in generate_tokens(get)][:-1]

########################
###   TOKENS
########################

class Tokens(object):
    def __init__(self, default_kls):
        self.default_kls = tokens_in(default_kls)

        self.equivalence = {
              'after_each' : 'tearDown'
            , 'before_each' : 'setUp'
            }

        self.before_each = [
              (NAME, 'def')
            , (NAME, self.equivalence['before_each'])
            , (OP, '(')
            , (NAME, 'self')
            , (OP, ')')
            ]

        self.after_each = [
              (NAME, 'def')
            , (NAME, self.equivalence['after_each'])
            , (OP, '(')
            , (NAME, 'self')
            , (OP, ')')
            ]

        self.test_skip = [
              (NAME, 'raise')
            , (NAME, 'nose.SkipTest')
            ]

    ########################
    ###   MAKERS
    ########################

    def make_single(self, name, args):
        lst = [ (NAME, 'def')
              , (NAME, name)
              , (OP, '(')
              ]

        if args:
            lst.extend(args[0])

            for arg in args[1:]:
                lst.append((OP, ','))
                lst.extend(arg)

        lst.extend(
            [ (OP, ')')
            , (OP, ':')
            ]
        )
        return lst

    def make_describe(self, kls, name):
        lst = [ (NAME, 'class')
                 , (NAME, name)
                 , (OP, '(')
                 ]
        if kls:
            lst.extend(tokens_in(kls))
        else:
            lst.extend(self.default_kls)

        lst.extend(
            [ (OP, ')')
            , (OP, ':')
            ]
        )

        return lst

    def make_super(self, indent, kls, method, with_async=False):
        if kls:
            kls = tokens_in(kls)
        else:
            kls = self.default_kls

        method_name = '%snoy_sup_%s' % ('async_' if with_async else '', self.equivalence[method])
        result = [ (OP, ':')
                 , (NEWLINE, '\n')
                 , (INDENT, indent)
                 ]

        if with_async:
            result.append((NAME, "await"))

        result.extend(
              [ (NAME, method_name)
              , (OP, '(')
              , (NAME, 'super')
              , (OP, '(')
              ]
            )

        result.extend(kls)

        result.extend(
            [ (OP, ',')
            , (NAME, 'self')
            , (OP, ')')
            , (OP, ')')
            ]
        )

        return result

    def make_describe_attr(self, describe):
        return [ (NEWLINE, '\n')
               , (NAME, describe)
               , (OP, '.')
               , (NAME, 'is_noy_spec')
               , (OP, '=')
               , (NAME, 'True')
               ]

    def make_name_modifier(self, ismethod, cleaned, english):
        result = [ (NEWLINE, '\n') ]

        parts = cleaned.split('.')
        result.append((NAME, parts[0]))

        for part in parts[1:]:
            result.extend(
                [ (OP, '.')
                , (NAME, part)
                ]
            )

        if ismethod and not six.PY3:
            result.extend(
                [ (OP, '.')
                , (NAME, "__func__")
                ]
            )

        result.extend(
            [ (OP, '.')
            , (NAME, "__testname__")
            , (OP, '=')
            , (STRING, english)
            ]
        )

        return result

    def wrap_setup(self, class_name, typ, with_async=False):
        """Described.typ = noy_wrap_typ(Described, Described.typ)"""
        equivalence = self.equivalence[typ]
        return [
              (NEWLINE, '\n')
            , (NAME, class_name)
            , (OP, '.')
            , (NAME, equivalence)
            , (OP, '=')
            , (NAME, "%snoy_wrap_%s" % ('async_' if with_async else '', equivalence))
            , (OP, "(")
            , (NAME, class_name)
            , (OP, ',')
            , (NAME, class_name)
            , (OP, '.')
            , (NAME, equivalence)
            , (OP, ")")
            ]

    def wrap_after_each(self, class_name, with_async=False):
        return self.wrap_setup(class_name, "after_each", with_async=with_async)

    def wrap_before_each(self, class_name, with_async=False):
        return self.wrap_setup(class_name, "before_each", with_async=with_async)

