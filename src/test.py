"""Just run "$nosetests" in the same folder as this file"""
from tokeniser import Tokeniser
from should_dsl import *
from tokenize import *
import cStringIO

########################
###   CUSTOM MATCHER
########################
    
@matcher
class ResultIn(object):

    name = 'result_in'

    def __call__(self, radicand):
        self._radicand = radicand
        return self

    def match(self, actual):
        tokeniser, self._actual = actual
        s = cStringIO.StringIO(self._actual)
        try:
            tokens = tokeniser.translate(s.readline)
            self._expected = untokenize(tokens)
        finally:
            s.close()
            
        return self._expected == self._radicand

    def message_for_failed_should(self):
        return 'expected "%s"\n\t=>  "%s"\n\tgot "%s"' % (
            self._actual, self._radicand, self._expected)

    def message_for_failed_should_not(self):
        return 'expected "%s"\n\tTo not translate to "%s"' % (
            self._actual, self._radicand)

########################
###   TESTS
########################

class Test_Tokeniser(object):
        
    def test_it_should_not_have_newline_in_default_imports(self):
        tok = Tokeniser()
        tok.defaultImports |should_not.contain| (NEWLINE, '\n')
        
    def test_it_should_not_have_newline_in_extended_default_imports(self):
        tok = Tokeniser(extraImports='import another.class')
        tok.defaultImports |should_not.contain| (NEWLINE, '\n')
        (tok, '') | should | result_in('import another .class ;import nose ;from nose .tools import *;from should_dsl import *')
    
    def test_it_should_default_to_giving_describes_base_of_object(self):
        tok = Tokeniser()
        tok.defaultKls |should.equal_to| [(NAME, 'object')]
    
    def test_it_should_handle_custom_base_class_for_describes(self):
        tok = Tokeniser(defaultKls='django.test.TestCase')
        tok.defaultKls |should.equal_to| [
              (NAME, 'django')
            , (OP,   '.')
            , (NAME, 'test')
            , (OP,   '.')
            , (NAME, 'TestCase')
            ]
    
    def test_it_should_be_possible_to_specify_no_default_imports(self):
        tok = Tokeniser(withDefaultImports=False)
        tok.defaultImports |should.equal_to| []
    
    def test_it_should_be_possible_to_specify_extra_imports_without_default_imports(self):
        tok = Tokeniser(withDefaultImports=False, extraImports="import thing")
        (tok, '') | should | result_in('import thing ;')
    
    def test_it_should_import_nose_and_should_dsl_by_default(self):
        (Tokeniser(), '') | should | result_in('import nose ;from nose .tools import *;from should_dsl import *')
    
class Test_Tokenisor_translation(object):
    def setUp(self):
        self.toka = Tokeniser(withDefaultImports=False)
        self.tokb = Tokeniser(withDefaultImports=False, defaultKls = 'other')
        
    def test_it_should_translate_a_describe(self):
        (self.toka, 'describe "Something testable"') | should | result_in('class Test_Something_testable (object )')
        (self.tokb, 'describe "Something testable"') | should | result_in('class Test_Something_testable (other )')
        
        # Same tests, but with newlines in front
        (self.toka, '\ndescribe "Something testable"') | should | result_in('\nclass Test_Something_testable (object )')
        (self.tokb, '\ndescribe "Something testable"') | should | result_in('\nclass Test_Something_testable (other )')
        
    def test_it_should_translate_an_it(self):
        (self.toka, 'it "should do this thing"') | should | result_in('def test_should_do_this_thing (self )')
        (self.tokb, 'it "should do this thing"') | should | result_in('def test_should_do_this_thing (self )')
        
        # Same tests, but with newlines in front
        (self.toka, '\nit "should do this thing"') | should | result_in('\ndef test_should_do_this_thing (self )')
        (self.tokb, '\nit "should do this thing"') | should | result_in('\ndef test_should_do_this_thing (self )')
        
    def test_it_should_turn_an_it_without_colon_into_skippable(self):
        (self.toka, 'it "should be skipped"\n') | should | result_in(
            'def test_should_be_skipped (self ):raise nose.SkipTest \n'
        )
        
        (self.toka, 'it "should not be skipped":\n') | should | result_in(
            'def test_should_not_be_skipped (self ):\n'
        )
        
        # Same tests, but with newlines in front
        (self.toka, '\nit "should be skipped"\n') | should | result_in(
            '\ndef test_should_be_skipped (self ):raise nose.SkipTest \n'
        )
        
        (self.toka, '\nit "should not be skipped":\n') | should | result_in(
            '\ndef test_should_not_be_skipped (self ):\n'
        )
        
    def test_it_should_turn_before_each_into_setUp(self):
        (self.toka, 'before_each:') | should | result_in('def setUp (self ):')
        
        # Same tests, but with newlines in front
        (self.toka, '\nbefore_each:') | should | result_in('\ndef setUp (self ):')
        
    def test_it_should_turn_after_each_into_tearDown(self):
        (self.toka, 'after_each:') | should | result_in('def tearDown (self ):')
        
        # Same tests, but with newlines in front
        (self.toka, '\nafter_each:') | should | result_in('\ndef tearDown (self ):')
    
    def test_it_should_have_ignorable_its(self):
        (self.toka, '\nignore "should be ignored"') | should | result_in('\ndef ignore__should_be_ignored (self )')
        (self.toka, '\nignore "should be ignored"') | should | result_in('\ndef ignore__should_be_ignored (self )')
    
    def test_it_should_not_transform_inside_expression(self):
        (self.toka, 'variable = before_each') | should | result_in('variable =before_each ')
        (self.toka, 'variable = after_each')  | should | result_in('variable =after_each ')
        (self.toka, 'variable = describe')    | should | result_in('variable =describe ')
        (self.toka, 'variable = ignore')      | should | result_in('variable =ignore ')
        (self.toka, 'variable = it')          | should | result_in('variable =it ')
        
        # Same tests, but with newlines in front
        (self.toka, '\nvariable = before_each') | should | result_in('\nvariable =before_each ')
        (self.toka, '\nvariable = after_each')  | should | result_in('\nvariable =after_each ')
        (self.toka, '\nvariable = describe')    | should | result_in('\nvariable =describe ')
        (self.toka, '\nvariable = ignore')      | should | result_in('\nvariable =ignore ')
        (self.toka, '\nvariable = it')          | should | result_in('\nvariable =it ')
    
    def test_it_should_allow_definition_of_different_base_class_for_next_describe(self):
        test = '''
        describe TestCase "This thing":pass
        describe "Another thing":pass
        '''
        
        desired = '''%s
        class Test_This_thing (TestCase ):pass 
        class Test_Another_thing (%s ):pass \n'''
        
        (self.toka, test) | should | result_in(desired % ('', 'object'))
        (self.tokb, test) | should | result_in(desired % ('', 'other'))
        
        # Same tests, but with newlines in front
        (self.toka, '\n%s' % test) | should | result_in(desired % ('\n', 'object'))
        (self.tokb, '\n%s' % test) | should | result_in(desired % ('\n', 'other'))
        
