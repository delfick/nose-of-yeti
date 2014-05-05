from noseOfYeti.tokeniser.tokens import tokens_in

from tokenize import OP, NEWLINE
import six

def determine_imports(with_default_imports=False, extra_imports=None):
    default = []

    if extra_imports:
        if isinstance(extra_imports, six.string_types):
            default.extend(tokens_in(extra_imports))
        else:
            for d in extra_imports:
                if d[0] == NEWLINE:
                    # I want to make sure the extra imports don't
                    # Take up extra lines in the code than the "# coding: spec"
                    default.append((OP, ';'))
                else:
                    default.append(d)

    if with_default_imports:
        if default and tuple(default[-1]) != (OP, ';'):
            default.append((OP, ';'))

        import_tokens = tokens_in('import nose; from nose.tools import *; from noseOfYeti.tokeniser.support import *')
        default.extend(import_tokens)

    return default

