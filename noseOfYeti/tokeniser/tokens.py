from tokenize import NAME, OP, INDENT, NEWLINE, DEDENT, STRING, ERRORTOKEN
from tokenize import generate_tokens

########################
###   TOKENS IN GENERATOR
########################
    
def tokensIn(s, strip_it=True):
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
    def __init__(self, defaultKls):
        self.defaultKls = tokensIn(defaultKls)
        self.constructReplacements()

    def getEquivalence(self, name):
        return { 'before_each' : 'setUp'
               , 'after_each'  : 'tearDown'
               }.get(name, name)

    ########################
    ###   Initializers
    ########################

    def constructReplacements(self):
        self.before_each = [
              (NAME, 'def')
            , (NAME, self.getEquivalence('before_each'))
            , (OP, '(')
            , (NAME, 'self')
            , (OP, ')')
            ]

        self.after_each = [
              (NAME, 'def')
            , (NAME, self.getEquivalence('after_each'))
            , (OP, '(')
            , (NAME, 'self')
            , (OP, ')')
            ]

        self.testSkip = [
              (OP, ':')
            , (NAME, 'raise')
            , (NAME, 'nose.SkipTest')
            ]

        self.endIt = [ (OP, ')')]

    ########################
    ###   MAKERS
    ########################

    def startFunction(self, funcName, withSelf=True):
        lst =  [
              (NAME, funcName)
            , (OP, '(')
            ]

        if withSelf:
            lst.append((NAME, 'self'))

        return lst

    def makeDescribe(self, name, value, nextDescribeKls, inheriting=False):
        if nextDescribeKls and inheriting:
            use = nextDescribeKls
            if use.startswith('Test'):
                use = use[4:]
            name = 'Test{0}_{1}'.format(use, name)
        else:
            name = 'Test{0}'.format(name)

        result = [ (NAME, name)
                 , (OP, '(')
                 ]
        if nextDescribeKls:
            result.extend(tokensIn(nextDescribeKls))
        else:
            result.extend(self.defaultKls)
        result.append((OP, ')'))
        return result, name

    def makeSuper(self, nextDescribeKls, method):
        if nextDescribeKls:
            kls = tokensIn(nextDescribeKls)
        else:
            kls = self.defaultKls

        result = [ (NAME, 'noy_sup_%s' % self.getEquivalence(method))
                 , (OP, '(')
                 , (NAME, 'super')
                 , (OP, '(')
                 ]

        result.extend(kls)

        result.extend(
            [ (OP, ',')
            , (NAME, 'self')
            , (OP, ')')
            , (OP, ')')
            , (OP, ';')
            ]
        )

        return result

    def makeDescribeAttr(self, describe):
        return [ (NEWLINE, '\n')
               , (NAME, describe)
               , (OP, '.')
               , (NAME, 'is_noy_spec')
               , (OP, '=')
               , (NAME, 'True')
               ]
   
    def makeNameModifier(self, kls, cleaned, english):
        result = [ (NEWLINE, '\n') ]
        
        if kls:
            result.extend(
                [ (NAME, kls)
                , (OP, '.')
                ]
            )

        result.append((NAME, cleaned))

        if kls:
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