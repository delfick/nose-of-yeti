from noseOfYeti.tokeniser import Tokeniser, determineImports
from should_dsl import *
from matchers import *

class Test_Tokeniser(object):
    
    def test_it_should_give_describes_noy_specific_attributes(self):
        imports = determineImports(withDefaultImports=False)
        tok = Tokeniser(importTokens = imports)
        (tok, 'describe "Something testable"') |should| result_in(
        '''class TestSomethingTestable (object )

TestSomethingTestable .is_noy_spec =True '''
        )
    
    def test_it_should_be_possible_to_turn_off_attributes(self):
        imports = determineImports(withDefaultImports=False)
        tok = Tokeniser(importTokens=imports, withDescribeAttrs=False)
        (tok, 'describe "Something testable"') |should| result_in('class TestSomethingTestable (object )')
    
    def test_it_should_not_have_newline_in_default_imports(self):
        tok = Tokeniser(importTokens=determineImports())
        tok.importTokens |should_not| contain([NEWLINE, '\n'])
        
    def test_it_should_not_have_newline_in_extended_default_imports(self):
        imports = determineImports(extraImports='import another.class')
        tok = Tokeniser(importTokens=imports)
        tok.importTokens |should_not| contain([NEWLINE, '\n'])
        (tok, '') |should| result_in('import another .class ;import nose ;from nose .tools import *;from should_dsl import *;from noseOfYeti .noy_helper import *;')
    
    def test_it_should_default_to_giving_describes_base_of_object(self):
        tok = Tokeniser()
        tok.tokens.defaultKls |should| equal_to([(NAME, 'object')])
    
    def test_it_should_handle_custom_base_class_for_describes(self):
        tok = Tokeniser(defaultKls='django.test.TestCase')
        tok.tokens.defaultKls |should| equal_to([
              (NAME, 'django')
            , (OP,   '.')
            , (NAME, 'test')
            , (OP,   '.')
            , (NAME, 'TestCase')
            ])
    
    def test_it_should_have_no_default_imports_by_default(self):
        tok = Tokeniser()
        tok.importTokens |should| equal_to(None)
    
    def test_it_should_be_possible_to_specify_extra_imports_without_default_imports(self):
        imports = determineImports(withDefaultImports=False, extraImports="import thing")
        tok = Tokeniser(importTokens = imports)
        (tok, '') |should| result_in('import thing ')
    
    def test_it_should_import_nose_and_nose_helpers_and_should_dsl_by_default(self):
        imports = determineImports()
        tok = Tokeniser(importTokens=imports)
        (tok, '') |should| result_in('import nose ;from nose .tools import *;from should_dsl import *;from noseOfYeti .noy_helper import *;')