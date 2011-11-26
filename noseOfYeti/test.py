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
        return 'expected "{0}"\n======================>\n"{1}"\n\n======================$\n"{2}"'.format(
            *(res.replace(' ', '.').replace('\t', '-') for res in (self._actual, self._radicand, self._expected)))

    def message_for_failed_should_not(self):
        return 'expected "{0}"\n\tTo not translate to "{1}"'.format(
            *(res.replace(' ', '.').replace('\t', '-') for res in (self._actual, self._radicand)))

########################
###   GENERAL TESTS
########################

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
   
########################
###   TRANSLATION TESTS
########################
 
class Test_Tokenisor_translation(object):
    def setUp(self):
        self.toka = Tokeniser(withDefaultImports=False, withDescribeAttrs=False)
        self.tokb = Tokeniser(withDefaultImports=False, withDescribeAttrs=False, defaultKls = 'other')
        
    def test_it_should_translate_a_describe(self):
        (self.toka, 'describe "Something testable"') |should| result_in('class TestSomethingTestable (object )')
        (self.tokb, 'describe "Something testable"') |should| result_in('class TestSomethingTestable (other )')
        
        # Same tests, but with newlines in front
        (self.toka, '\ndescribe "Something testable"') |should| result_in('\nclass TestSomethingTestable (object )')
        (self.tokb, '\ndescribe "Something testable"') |should| result_in('\nclass TestSomethingTestable (other )')
        
    def test_it_should_translate_an_it(self):
        (self.toka, 'it "should do this thing":') |should| result_in('def test_should_do_this_thing (self ):')
        (self.tokb, 'it "should do this thing":') |should| result_in('def test_should_do_this_thing (self ):')
        
        # Same tests, but with newlines in front
        (self.toka, '\nit "should do this thing":') |should| result_in('\ndef test_should_do_this_thing (self ):')
        (self.tokb, '\nit "should do this thing":') |should| result_in('\ndef test_should_do_this_thing (self ):')
    
    def test_it_should_add_arguments_to_its_if_declared_on_same_line(self):
        (self.toka, 'it "should do this thing", blah, meh:') |should| result_in(
            'def test_should_do_this_thing (self ,blah ,meh ):'
            )
        (self.tokb, 'it "should do this thing", blah, meh:') |should| result_in(
            'def test_should_do_this_thing (self ,blah ,meh ):'
            )
        
        # Same tests, but with newlines in front
        (self.toka, '\nit "should do this thing", blah, meh:') |should| result_in(
            '\ndef test_should_do_this_thing (self ,blah ,meh ):'
            )
        (self.tokb, '\nit "should do this thing", blah, meh:') |should| result_in(
            '\ndef test_should_do_this_thing (self ,blah ,meh ):'
            )    
    def test_it_should_add_arguments_to_its_if_declared_on_same_line_and_work_with_skipTest(self):
        (self.toka, 'it "should do this thing", blah, meh') |should| result_in(
            'def test_should_do_this_thing (self ,blah ,meh ):raise nose.SkipTest '
            )
        (self.tokb, 'it "should do this thing", blah, meh') |should| result_in(
            'def test_should_do_this_thing (self ,blah ,meh ):raise nose.SkipTest '
            )
        
        # Same tests, but with newlines in front
        (self.toka, '\nit "should do this thing", blah, meh') |should| result_in(
            '\ndef test_should_do_this_thing (self ,blah ,meh ):raise nose.SkipTest '
            )
        (self.tokb, '\nit "should do this thing", blah, meh') |should| result_in(
            '\ndef test_should_do_this_thing (self ,blah ,meh ):raise nose.SkipTest '
            )
        
    def test_it_should__not_add_arguments_to_its_if_not_declared_on_same_line(self):
        (self.toka, 'it "should do this thing"\n, blah, meh') |should| result_in(
            "def test_should_do_this_thing (self ):raise nose.SkipTest \n,blah ,meh "
            )
        (self.tokb, 'it "should do this thing"\n, blah, meh') |should| result_in(
            "def test_should_do_this_thing (self ):raise nose.SkipTest \n,blah ,meh "
            )
        
        # Same tests, but with newlines in front
        (self.toka, '\nit "should do this thing"\n, blah, meh') |should| result_in(
            "\ndef test_should_do_this_thing (self ):raise nose.SkipTest \n,blah ,meh "
            )
        (self.tokb, '\nit "should do this thing"\n, blah, meh') |should| result_in(
            "\ndef test_should_do_this_thing (self ):raise nose.SkipTest \n,blah ,meh "
            )
        
    def test_it_should_turn_an_it_without_colon_into_skippable(self):
        (self.toka, 'it "should be skipped"\n') |should| result_in(
            'def test_should_be_skipped (self ):raise nose.SkipTest '
        )
        
        (self.toka, 'it "should not be skipped":\n') |should| result_in(
            'def test_should_not_be_skipped (self ):'
        )
        
        # Same tests, but with newlines in front
        (self.toka, '\nit "should be skipped"\n') |should| result_in(
            '\ndef test_should_be_skipped (self ):raise nose.SkipTest '
        )
        
        (self.toka, '\nit "should not be skipped":\n') |should| result_in(
            '\ndef test_should_not_be_skipped (self ):'
        )
        
    def test_it_should_turn_before_each_into_setup(self):
        (self.toka, 'before_each:') |should| result_in('def setup (self ):')
        
        # Same tests, but with newlines in front
        (self.toka, '\nbefore_each:') |should| result_in('\ndef setup (self ):')
    
    def test_indentation_should_work_regardless_of_crazy_groups(self):
        test = """
        describe 'a':
            it 'asdf':
                l = [ True
                    , False
                        , 1
                , 2
                ]
                
                t = (1
                        , 2
                , 3
            , 4
                    , 5,
                )
                
                d = {'asdf' : True}
                
                t2 = (True
                ,    False
        )
            it 'asdf2'"""
        
        desired = """
class TestA (object ):
    def test_asdf (self ):
        l =[True 
        ,False 
        ,1 
        ,2 
        ]

        t =(1 
        ,2 
        ,3 
        ,4 
        ,5 ,
        )

        d ={'asdf':True }

        t2 =(True 
        ,False 
        )
    def test_asdf2 (self ):raise nose.SkipTest """
    
        (self.toka, test) |should| result_in(desired)
            
    def test_indentation_for_test_should_work_after_skipped_test(self):
        test = """
        describe 'thing':
            it 'should be skipped'
            it 'shouldnt be skipped':
                print 'hi'
            
            it 'another that should be skipped'
            
            it 'another that shouldnt be skipped':
                print 'hi'"""
        
        desired = """
class TestThing (object ):
    def test_should_be_skipped (self ):raise nose.SkipTest 
    def test_shouldnt_be_skipped (self ):
        print 'hi'

    def test_another_that_should_be_skipped (self ):raise nose.SkipTest 

    def test_another_that_shouldnt_be_skipped (self ):
        print 'hi'"""
        
        (self.toka, test) |should| result_in(desired)
    
    def test_indentation_for_describe_should_work_after_skipped_test(self):
        test = '''
        describe 'thing':
            it 'should be skipped'
            describe 'that':
                pass'''
        
        desired = '''
class TestThing (object ):
    def test_should_be_skipped (self ):raise nose.SkipTest 
class TestThing_That (TestThing ):
    pass '''
        (self.toka, test) |should| result_in(desired)
        
    def test_indentation_should_work_for_inline_python_code(self):
        test = '''
describe 'this':
    describe 'that':
        pass

class SomeMockObject(object):
    def indented_method()'''

        desired = '''
class TestThis (object ):pass 
class TestThis_That (TestThis ):
    pass 

class SomeMockObject (object ):
    def indented_method ()'''
        (self.toka, test) | should | result_in(desired)

    def test_it_should_give_setups_super_call_when_in_describes(self):
        test = '''
        describe "Thing":
            before_each:
                self.x = 5
        '''
        
        desired = '''
class TestThing (object ):
    def setup (self ):
        noy_sup_setup (super (TestThing ,self ));self .x =5 '''
        
        (self.toka, test) |should| result_in(desired)
        # and with tabs
        (self.toka, test.replace('    ', '\t')) |should| result_in(desired.replace('    ', '\t'))
        
    def test_it_should_turn_after_each_into_teardown(self):
        (self.toka, 'after_each:') |should| result_in('def teardown (self ):')
        
        # Same tests, but with newlines in front
        (self.toka, '\nafter_each:') |should| result_in('\ndef teardown (self ):')
    
    def test_it_should_give_teardowns_super_call_when_in_describes(self):
        test = '''
        describe "Thing":
            after_each:
                self.x = 5
        '''
        
        desired = '''
class TestThing (object ):
    def teardown (self ):
        noy_sup_teardown (super (TestThing ,self ));self .x =5 '''
        
        (self.toka, test) |should| result_in(desired)
        # and with tabs
        (self.toka, test.replace('    ', '\t')) |should| result_in(desired.replace('    ', '\t'))
    
    def test_it_should_have_ignorable_its(self):
        (self.toka, '\nignore "should be ignored"') |should| result_in(
            '\ndef ignore__should_be_ignored (self ):raise nose.SkipTest '
            )
        (self.toka, '\nignore "should be ignored"') |should| result_in(
            '\ndef ignore__should_be_ignored (self ):raise nose.SkipTest '
            )
    
    def test_it_should_not_transform_inside_expression(self):
        (self.toka, 'variable = before_each') |should| result_in('variable =before_each ')
        (self.toka, 'variable = after_each')  |should| result_in('variable =after_each ')
        (self.toka, 'variable = describe')    |should| result_in('variable =describe ')
        (self.toka, 'variable = ignore')      |should| result_in('variable =ignore ')
        (self.toka, 'variable = it')          |should| result_in('variable =it ')
        
        # Same tests, but with newlines in front
        (self.toka, '\nvariable = before_each') |should| result_in('\nvariable =before_each ')
        (self.toka, '\nvariable = after_each')  |should| result_in('\nvariable =after_each ')
        (self.toka, '\nvariable = describe')    |should| result_in('\nvariable =describe ')
        (self.toka, '\nvariable = ignore')      |should| result_in('\nvariable =ignore ')
        (self.toka, '\nvariable = it')          |should| result_in('\nvariable =it ')
    
    def test_it_should_allow_definition_of_different_base_class_for_next_describe(self):
        test = '''
        describe unittest.TestCase "This thing":pass
        describe "Another thing":pass
        '''
        
        desired = '''%s
class TestThisThing (unittest .TestCase ):pass 
class TestAnotherThing (%s ):pass '''
        
        (self.toka, test) |should| result_in(desired % ('', 'object'))
        (self.tokb, test) |should| result_in(desired % ('', 'other'))
        
        # Same tests, but with newlines in front
        (self.toka, '\n%s' % test) |should| result_in(desired % ('\n', 'object'))
        (self.tokb, '\n%s' % test) |should| result_in(desired % ('\n', 'other'))
    
    def test_it_should_set__testname__on_non_alphanumeric_test_names(self):
        test = '''
        it "(root level) should work {well}"
            3 |should| be(4)
        describe "SomeTests":
            it "doesn't get phased by $special characters"
            
            describe "NestedDescribe":
                it "asdf $% asdf":
                    1 |should| be(2)
        it "(root level) should also [work]"
        '''
        
        desired = '''
        def test_root_level_should_work_well (self ):raise nose.SkipTest 
            3 |should |be (4 )
class TestSomeTests (%s ):
    def test_doesnt_get_phased_by_special_characters (self ):raise nose.SkipTest 

class TestSomeTests_NestedDescribe (TestSomeTests ):
    def test_asdf_asdf (self ):
        1 |should |be (2 )
def test_root_level_should_also_work (self ):raise nose.SkipTest 
test_root_level_should_work_well .__testname__ ="(root level) should work {well}"
test_root_level_should_also_work .__testname__ ="(root level) should also [work]"
TestSomeTests_NestedDescribe .test_asdf_asdf .__testname__ ="asdf $%% asdf"
TestSomeTests .test_doesnt_get_phased_by_special_characters .__testname__ ="doesn't get phased by $special characters"'''
        (self.toka, test) |should| result_in(desired % "object")
        (self.tokb, test) |should| result_in(desired % "other")
        
########################
###   NESTING TESTS
########################
 
class Test_Tokeniser_Nesting(object):
    def setUp(self):
        self.toka = Tokeniser(withDefaultImports=False, withDescribeAttrs=False)
        self.tokb = Tokeniser(withDefaultImports=False, withDescribeAttrs=False, defaultKls = 'other')
        
        ###   SMALL EXAMPLE (WITHOUT PASS)
        
        self.smallExample = [
        '''
        describe "This":
            describe "That":

                describe "Meh":pass
            context "Blah":pass
        describe "Another":pass '''
        ,
        '''
class TestThis (%(o)s ):pass 
class TestThis_That (TestThis ):pass 
class TestThis_That_Meh (TestThis_That ):pass 
class TestThis_Blah (TestThis ):pass 
class TestAnother (%(o)s ):pass '''
        ]
        
        ###   SMALL EXAMPLE (WITH PATH FOR BW COMPAT)
        
        self.smallExampleWithPass = [
        '''
        context "This":pass
            describe "That":pass
                describe "Meh":pass
            describe "Blah":pass
        describe "Another":pass '''
        ,
        '''
class TestThis (%(o)s ):pass 
class TestThis_That (TestThis ):pass 
class TestThis_That_Meh (TestThis_That ):pass 
class TestThis_Blah (TestThis ):pass 
class TestAnother (%(o)s ):pass '''
        ]
        
        ###   BIG EXAMPLE
        
        self.bigExample = [
        '''
        describe "This":
            it 'should':
                if x:
                    pass
                else:
                    x += 9
            describe "That":
                describe "Meh":
                    it 'should':
                        if y:
                            pass
                        else:
                            pass
            describe "Blah":pass
        describe "Another":
            it 'should':
                if z:
                    if u:
                        print "hello \
                            there"
                    else:
                        print "no"
                else:
                    pass
        '''
        ,
        '''
class TestThis (%(o)s ):
    def test_should (self ):
        if x :
            pass 
        else :
            x +=9 
class TestThis_That (TestThis ):pass 
class TestThis_That_Meh (TestThis_That ):
    def test_should (self ):
        if y :
            pass 
        else :
            pass 
class TestThis_Blah (TestThis ):pass 
class TestAnother (%(o)s ):
    def test_should (self ):
        if z :
            if u :
                print "hello \
                            there"
            else :
                print "no"
        else :
            pass '''
        ]
        
    ###   TESTS
    
    def test_it_should_work_with_space(self):
        test, desired = self.smallExample
        (self.toka, test) |should| result_in(desired % {'o' : 'object'})
        (self.tokb, test) |should| result_in(desired % {'o' : 'other'})
    
    def test_it_should_work_with_tabs(self):
        test, desired = [d.replace('    ', '\t') for d in self.smallExample]
        (self.toka, test) |should| result_in(desired % {'o' : 'object'})
        (self.tokb, test) |should| result_in(desired % {'o' : 'other'})
        
    def test_it_should_work_with_space_and_inline_pass(self):
        test, desired = self.smallExampleWithPass
        (self.toka, test) |should| result_in(desired % {'o' : 'object'})
        (self.tokb, test) |should| result_in(desired % {'o' : 'other'})
    
    def test_it_should_work_with_tabs_and_inline_pass(self):
        test, desired = [d.replace('    ', '\t') for d in self.smallExampleWithPass]
        (self.toka, test) |should| result_in(desired % {'o' : 'object'})
        (self.tokb, test) |should| result_in(desired % {'o' : 'other'})
        
    def test_it_should_keep_good_indentation_in_body_with_spaces(self):
        test, desired = self.bigExample
        (self.toka, test) |should| result_in(desired % {'o' : 'object'})
        (self.tokb, test) |should| result_in(desired % {'o' : 'other'})
        
    def test_it_should_keep_good_indentation_in_body_with_tabs(self):
        test, desired = [d.replace('    ', '\t') for d in self.bigExample]
        (self.toka, test) |should| result_in(desired % {'o' : 'object'})
        (self.tokb, test) |should| result_in(desired % {'o' : 'other'})
    
    def test_it_should_name_nested_describes_with_part_of_parents_name(self):
        test = 'describe "a":\n\tdescribe "b":'
        desired = 'class TestA (object ):pass \nclass TestA_B (TestA ):'
        (self.toka, test) |should| result_in(desired)
    
########################
###   MORE NESTING TESTS
########################
 
class Test_Tokeniser_More_Nesting(object):
    def setUp(self):
        self.toka = Tokeniser(withDefaultImports=False)
        self.tokb = Tokeniser(withDefaultImports=False, defaultKls = 'other')
        
        ###   SMALL EXAMPLE
        
        self.smallExample = [
        '''
        describe "This":
            before_each:
                self.x = 5
            describe "That":
                before_each:
                    self.y = 6
                describe "Meh":
                    after_each:
                        self.y = None
            describe "Blah":pass
        describe "Another":
            before_each:
                self.z = 8 '''
        ,
        '''
class TestThis (%(o)s ):
    def setup (self ):
        noy_sup_setup (super (TestThis ,self ));self .x =5 
class TestThis_That (TestThis ):
    def setup (self ):
        noy_sup_setup (super (TestThis_That ,self ));self .y =6 
class TestThis_That_Meh (TestThis_That ):
    def teardown (self ):
        noy_sup_teardown (super (TestThis_That_Meh ,self ));self .y =None 
class TestThis_Blah (TestThis ):pass 
class TestAnother (%(o)s ):
    def setup (self ):
        noy_sup_setup (super (TestAnother ,self ));self .z =8 

TestThis .is_noy_spec =True 
TestThis_That .is_noy_spec =True 
TestThis_That_Meh .is_noy_spec =True 
TestThis_Blah .is_noy_spec =True 
TestAnother .is_noy_spec =True '''
        ]
        
        ###   BIG EXAMPLE
        
        self.bigExample = [
        '''
        describe "This":
            before_each:
                self.x = 5
            it 'should':
                if x:
                    pass
                else:
                    x += 9
            describe "That":
                before_each:
                    self.y = 6
                describe "Meh":
                    after_each:
                        self.y = None
                    it "should set __testname__ for non alpha names ' $^":
                        pass
                    it 'should':
                        if y:
                            pass
                        else:
                            pass
                    it 'should have args', arg1, arg2:
                        blah |should| be_good()
            describe "Blah":pass
        ignore "root level $pecial-method*+"
        describe "Another":
            before_each:
                self.z = 8
            it 'should':
                if z:
                    if u:
                        print "hello \
                            there"
                    else:
                        print "no"
                else:
                    pass
        '''
        ,
        '''
class TestThis (%(o)s ):
    def setup (self ):
        noy_sup_setup (super (TestThis ,self ));self .x =5 
    def test_should (self ):
        if x :
            pass 
        else :
            x +=9 
class TestThis_That (TestThis ):
    def setup (self ):
        noy_sup_setup (super (TestThis_That ,self ));self .y =6 
class TestThis_That_Meh (TestThis_That ):
    def teardown (self ):
        noy_sup_teardown (super (TestThis_That_Meh ,self ));self .y =None 
    def test_should_set_testname_for_non_alpha_names (self ):
        pass 
    def test_should (self ):
        if y :
            pass 
        else :
            pass 
    def test_should_have_args (self ,arg1 ,arg2 ):
        blah |should |be_good ()
class TestThis_Blah (TestThis ):pass 
def ignore__root_level_pecial_method (self ):raise nose.SkipTest 
class TestAnother (%(o)s ):
    def setup (self ):
        noy_sup_setup (super (TestAnother ,self ));self .z =8 
    def test_should (self ):
        if z :
            if u :
                print "hello \
                            there"
            else :
                print "no"
        else :
            pass 

TestThis .is_noy_spec =True 
TestThis_That .is_noy_spec =True 
TestThis_That_Meh .is_noy_spec =True 
TestThis_Blah .is_noy_spec =True 
TestAnother .is_noy_spec =True 
ignore__root_level_pecial_method .__testname__ ="root level $pecial-method*+"
TestThis_That_Meh .test_should_set_testname_for_non_alpha_names .__testname__ ="should set __testname__ for non alpha names ' $^"'''
        ]
        
    ###   TESTS
    
    def test_it_should_work_with_space(self):
        test, desired = self.smallExample
        (self.toka, test) |should| result_in(desired % {'o' : 'object'})
        (self.tokb, test) |should| result_in(desired % {'o' : 'other'})
    
    def test_it_should_work_with_tabs(self):
        test, desired = [d.replace('    ', '\t') for d in self.smallExample]
        (self.toka, test) |should| result_in(desired % {'o' : 'object'})
        (self.tokb, test) |should| result_in(desired % {'o' : 'other'})
        
    def test_it_should_keep_good_indentation_in_body_with_spaces(self):
        test, desired = self.bigExample
        (self.toka, test) |should| result_in(desired % {'o' : 'object'})
        (self.tokb, test) |should| result_in(desired % {'o' : 'other'})
        
    def test_it_should_keep_good_indentation_in_body_with_tabs(self):
        test, desired = [d.replace('    ', '\t') for d in self.bigExample]
        (self.toka, test) |should| result_in(desired % {'o' : 'object'})
        (self.tokb, test) |should| result_in(desired % {'o' : 'other'})
