from tokenize import NAME, OP, INDENT, NEWLINE, DEDENT, STRING, ERRORTOKEN
from tokenize import generate_tokens

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
    
    def make_super(self, indent, kls, method):
        if kls:
            kls = tokens_in(kls)
        else:
            kls = self.default_kls
            
        method_name = 'noy_sup_%s' % self.equivalence[method]
        result = [ (OP, ':')
                 , (NEWLINE, '\n')
                 , (INDENT, indent)
                 , (NAME, method_name)
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