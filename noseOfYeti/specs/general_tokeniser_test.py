from noseOfYeti.tokeniser import Tokeniser
from should_dsl import *
from matchers import *

class Test_Tokeniser(object):
    
    def test_it_should_give_describes_noy_specific_attributes(self):
        tok = Tokeniser(withDefaultImports=False)
        (tok, 'describe "Something testable"') |should| result_in(
        '''class TestSomethingTestable (object )

TestSomethingTestable .is_noy_spec =True '''
        )
    
    def test_it_should_be_possible_to_turn_off_attributes(self):
        tok = Tokeniser(withDefaultImports=False, withDescribeAttrs=False)
        (tok, 'describe "Something testable"') |should| result_in('class TestSomethingTestable (object )')
    
    def test_it_should_not_have_newline_in_default_imports(self):
        tok = Tokeniser()
        tok.defaultImports |should_not| contain([NEWLINE, '\n'])
        
    def test_it_should_not_have_newline_in_extended_default_imports(self):
        tok = Tokeniser(extraImports='import another.class')
        tok.defaultImports |should_not| contain([NEWLINE, '\n'])
        (tok, '') |should| result_in('import another .class ;import nose ;from nose .tools import *;from should_dsl import *;from noseOfYeti .noy_helper import *;')
    
    def test_it_should_default_to_giving_describes_base_of_object(self):
        tok = Tokeniser()
        tok.defaultKls |should| equal_to([(NAME, 'object')])
    
    def test_it_should_handle_custom_base_class_for_describes(self):
        tok = Tokeniser(defaultKls='django.test.TestCase')
        tok.defaultKls |should| equal_to([
              (NAME, 'django')
            , (OP,   '.')
            , (NAME, 'test')
            , (OP,   '.')
            , (NAME, 'TestCase')
            ])
    
    def test_it_should_be_possible_to_specify_no_default_imports(self):
        tok = Tokeniser(withDefaultImports=False)
        tok.defaultImports |should| equal_to([])
    
    def test_it_should_be_possible_to_specify_extra_imports_without_default_imports(self):
        tok = Tokeniser(withDefaultImports=False, extraImports="import thing")
        (tok, '') |should| result_in('import thing ')
    
    def test_it_should_import_nose_and_nose_helpers_and_should_dsl_by_default(self):
        (Tokeniser(), '') |should| result_in('import nose ;from nose .tools import *;from should_dsl import *;from noseOfYeti .noy_helper import *;')