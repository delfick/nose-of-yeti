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
              (NAME, 'raise')
            , (NAME, 'nose.SkipTest')
            ]

        self.endIt = [ (OP, ')')]

    ########################
    ###   MAKERS
    ########################

    def makeSingle(self, name, args):
        lst = [ (NAME, 'def')
              , (NAME, name)
              , (OP, '(')
              ]
            
        if args:
            lst.append((NAME, args[0]))
            
            for arg in args[1:]:
                lst.extend(
                    [ (OP, ',')
                    , (NAME, arg)
                    ]
                )
        
        lst.extend(
            [ (OP, ')')
            , (OP, ':')
            ]
        )
        return lst

    def makeDescribe(self, kls, name):
        lst = [ (NAME, 'class')
                 , (NAME, name)
                 , (OP, '(')
                 ]
        if kls:
            lst.extend(tokensIn(kls))
        else:
            lst.extend(self.defaultKls)
        
        lst.extend(
            [ (OP, ')')
            , (OP, ':')
            ]
        )
        
        return lst

    def makeSuper(self, indent, kls, method):
        if kls:
            kls = tokensIn(kls)
        else:
            kls = self.defaultKls

        result = [ (OP, ':')
                 , (NEWLINE, '\n')
                 , (INDENT, indent)
                 , (NAME, 'noy_sup_%s' % self.getEquivalence(method))
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
   
    def makeNameModifier(self, ismethod, cleaned, english):
        result = [ (NEWLINE, '\n') ]
        
        parts = cleaned.split('.')
        result.append((NAME, parts[0]))
        
        for part in parts[1:]:
            result.extend(
                [ (OP, '.')
                , (NAME, part)
                ]
            )

        if ismethod:
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