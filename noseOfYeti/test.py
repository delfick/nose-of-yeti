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
        return 'expected "%s"\n======================>\n"%s"\n\n======================$\n"%s"' % (
            self._actual, self._radicand, self._expected)

    def message_for_failed_should_not(self):
        return 'expected "%s"\n\tTo not translate to "%s"' % (
            self._actual, self._radicand)

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
        (tok, '') |should| result_in('import another .class ;import nose ;from nose .tools import *;from should_dsl import *')
    
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
    
    def test_it_should_import_nose_and_should_dsl_by_default(self):
        (Tokeniser(), '') |should| result_in('import nose ;from nose .tools import *;from should_dsl import *')
   
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
        
    def test_it_should_turn_before_each_into_setUp(self):
        (self.toka, 'before_each:') |should| result_in('def setUp (self ):')
        
        # Same tests, but with newlines in front
        (self.toka, '\nbefore_each:') |should| result_in('\ndef setUp (self ):')
    
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
        
    def test_it_should_give_setups_super_call_when_in_describes(self):
        test = '''
        describe "Thing":
            before_each:
                self.x = 5
        '''
        
        desired = '''
class TestThing (object ):
    def setUp (self ):
        sup =super (TestThing ,self )
        if hasattr (sup,"setUp"):sup .setUp ()
        self .x =5 '''
        
        (self.toka, test) |should| result_in(desired)
        # and with tabs
        (self.toka, test.replace('    ', '\t')) |should| result_in(desired.replace('    ', '\t'))
        
    def test_it_should_turn_after_each_into_tearDown(self):
        (self.toka, 'after_each:') |should| result_in('def tearDown (self ):')
        
        # Same tests, but with newlines in front
        (self.toka, '\nafter_each:') |should| result_in('\ndef tearDown (self ):')
    
    def test_it_should_give_tearDowns_super_call_when_in_describes(self):
        test = '''
        describe "Thing":
            after_each:
                self.x = 5
        '''
        
        desired = '''
class TestThing (object ):
    def tearDown (self ):
        sup =super (TestThing ,self )
        if hasattr (sup,"tearDown"):sup .tearDown ()
        self .x =5 '''
        
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
        describe TestCase "This thing":pass
        describe "Another thing":pass
        '''
        
        desired = '''%s
class TestThisThing (TestCase ):pass 
class TestAnotherThing (%s ):pass '''
        
        (self.toka, test) |should| result_in(desired % ('', 'object'))
        (self.tokb, test) |should| result_in(desired % ('', 'other'))
        
        # Same tests, but with newlines in front
        (self.toka, '\n%s' % test) |should| result_in(desired % ('\n', 'object'))
        (self.tokb, '\n%s' % test) |should| result_in(desired % ('\n', 'other'))
        
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
    def setUp (self ):
        sup =super (TestThis ,self )
        if hasattr (sup,"setUp"):sup .setUp ()
        self .x =5 
class TestThis_That (TestThis ):
    def setUp (self ):
        sup =super (TestThis_That ,self )
        if hasattr (sup,"setUp"):sup .setUp ()
        self .y =6 
class TestThis_That_Meh (TestThis_That ):
    def tearDown (self ):
        sup =super (TestThis_That_Meh ,self )
        if hasattr (sup,"tearDown"):sup .tearDown ()
        self .y =None 
class TestThis_Blah (TestThis ):pass 
class TestAnother (%(o)s ):
    def setUp (self ):
        sup =super (TestAnother ,self )
        if hasattr (sup,"setUp"):sup .setUp ()
        self .z =8 

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
                    it 'should':
                        if y:
                            pass
                        else:
                            pass
                    it 'should have args', arg1, arg2:
                        blah |should| be_good()
            describe "Blah":pass
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
    def setUp (self ):
        sup =super (TestThis ,self )
        if hasattr (sup,"setUp"):sup .setUp ()
        self .x =5 
    def test_should (self ):
        if x :
            pass 
        else :
            x +=9 
class TestThis_That (TestThis ):
    def setUp (self ):
        sup =super (TestThis_That ,self )
        if hasattr (sup,"setUp"):sup .setUp ()
        self .y =6 
class TestThis_That_Meh (TestThis_That ):
    def tearDown (self ):
        sup =super (TestThis_That_Meh ,self )
        if hasattr (sup,"tearDown"):sup .tearDown ()
        self .y =None 
    def test_should (self ):
        if y :
            pass 
        else :
            pass 
    def test_should_have_args (self ,arg1 ,arg2 ):
        blah |should |be_good ()
class TestThis_Blah (TestThis ):pass 
class TestAnother (%(o)s ):
    def setUp (self ):
        sup =super (TestAnother ,self )
        if hasattr (sup,"setUp"):sup .setUp ()
        self .z =8 
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
TestAnother .is_noy_spec =True '''
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
