from tokenize import OP, NEWLINE
from tokens import tokensIn

def determineImports(withDefaultImports=True, withoutShouldDsl=False, extraImports=None):
    default = []

    if extraImports:
        if type(extraImports) in (str, unicode):
            default.extend(tokensIn(extraImports))
        else:
            for d in extraImports:
                if d[0] == NEWLINE:
                    # I want to make sure the extra imports don't 
                    # Take up extra lines in the code than the "# coding: spec"
                    default.append((OP, ';'))
                else:
                    default.append(d)

    if withDefaultImports:
        if default and tuple(default[-1]) != (OP, ';'):
            default.append((OP, ';'))

        should_dsl = "from should_dsl import *;"
        if withoutShouldDsl:
            should_dsl = ""
        
        default.extend(
            tokensIn('import nose; from nose.tools import *; %s from noseOfYeti.noy_helper import *;' % should_dsl)
        )

    return default