from noseOfYeti.tokeniser import Tokeniser
from should_dsl import *
from matchers import *

class Test_Tokenisor_translation(object):
    def setUp(self):
        self.toka = Tokeniser(with_describe_attrs=False)
        self.tokb = Tokeniser(with_describe_attrs=False, default_kls = 'other')
    
    def test_it_should_translate_a_describe(self):
        (self.toka, 'describe "Something testable"') |should| result_in('class TestSomethingTestable (object ):pass')
        (self.tokb, 'describe "Something testable"') |should| result_in('class TestSomethingTestable (other ):pass')
        
        # Same tests, but with newlines in front
        (self.toka, '\ndescribe "Something testable"') |should| result_in('\nclass TestSomethingTestable (object ):pass')
        (self.tokb, '\ndescribe "Something testable"') |should| result_in('\nclass TestSomethingTestable (other ):pass')
    
    def test_it_should_translate_an_it(self):
        (self.toka, 'it "should do this thing":') |should| result_in('def test_should_do_this_thing ():')
        (self.tokb, 'it "should do this thing":') |should| result_in('def test_should_do_this_thing ():')
        
        # Same tests, but with newlines in front
        (self.toka, '\nit "should do this thing":') |should| result_in('\ndef test_should_do_this_thing ():')
        (self.tokb, '\nit "should do this thing":') |should| result_in('\ndef test_should_do_this_thing ():')
    
    def test_it_should_add_arguments_to_its_if_declared_on_same_line(self):
        (self.toka, 'it "should do this thing", blah, meh:') |should| result_in(
            'def test_should_do_this_thing (blah ,meh ):'
            )
        (self.tokb, 'it "should do this thing", blah, meh:') |should| result_in(
            'def test_should_do_this_thing (blah ,meh ):'
            )
        
        # Same tests, but with newlines in front
        (self.toka, '\nit "should do this thing", blah, meh:') |should| result_in(
            '\ndef test_should_do_this_thing (blah ,meh ):'
            )
        (self.tokb, '\nit "should do this thing", blah, meh:') |should| result_in(
            '\ndef test_should_do_this_thing (blah ,meh ):'
            )
    
    def test_it_should_add_arguments_to_its_if_declared_on_same_line_and_work_with_skipTest(self):
        (self.toka, 'it "should do this thing", blah, meh') |should| result_in(
            'def test_should_do_this_thing (blah ,meh ):raise nose.SkipTest '
            )
        (self.tokb, 'it "should do this thing", blah, meh') |should| result_in(
            'def test_should_do_this_thing (blah ,meh ):raise nose.SkipTest '
            )
        
        # Same tests, but with newlines in front
        (self.toka, '\nit "should do this thing", blah, meh') |should| result_in(
            '\ndef test_should_do_this_thing (blah ,meh ):raise nose.SkipTest '
            )
        (self.tokb, '\nit "should do this thing", blah, meh') |should| result_in(
            '\ndef test_should_do_this_thing (blah ,meh ):raise nose.SkipTest '
            )
    
    def test_it_should__not_add_arguments_to_its_if_not_declared_on_same_line(self):
        (self.toka, 'it "should do this thing"\n, blah, meh') |should| result_in(
            "def test_should_do_this_thing ():raise nose.SkipTest \n,blah ,meh "
            )
        (self.tokb, 'it "should do this thing"\n, blah, meh') |should| result_in(
            "def test_should_do_this_thing ():raise nose.SkipTest \n,blah ,meh "
            )
        
        # Same tests, but with newlines in front
        (self.toka, '\nit "should do this thing"\n, blah, meh') |should| result_in(
            "\ndef test_should_do_this_thing ():raise nose.SkipTest \n,blah ,meh "
            )
        (self.tokb, '\nit "should do this thing"\n, blah, meh') |should| result_in(
            "\ndef test_should_do_this_thing ():raise nose.SkipTest \n,blah ,meh "
            )
    
    def test_it_should_turn_an_it_without_colon_into_skippable(self):
        (self.toka, 'it "should be skipped"\n') |should| result_in(
            'def test_should_be_skipped ():raise nose.SkipTest '
        )
        
        (self.toka, 'it "should not be skipped":\n') |should| result_in(
            'def test_should_not_be_skipped ():'
        )
        
        # Same tests, but with newlines in front
        (self.toka, '\nit "should be skipped"\n') |should| result_in(
            '\ndef test_should_be_skipped ():raise nose.SkipTest '
        )
        
        (self.toka, '\nit "should not be skipped":\n') |should| result_in(
            '\ndef test_should_not_be_skipped ():'
        )
    
    def test_it_should_turn_before_each_into_setup(self):
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
            def test_asdf2 (self ):raise nose.SkipTest 
        """
    
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
                print 'hi'
        """
        
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
            pass 
        '''
        (self.toka, test) |should| result_in(desired)
        
    def test_indentation_should_work_for_inline_python_code(self):
        test = '''
        describe 'this':
            describe 'that':
                pass

        class SomeMockObject(object):
            def indented_method()
        '''

        desired = '''
        class TestThis (object ):pass 
        class TestThis_That (TestThis ):
            pass 

        class SomeMockObject (object ):
            def indented_method ()
        '''
        
        (self.toka, test) | should | result_in(desired)

    def test_it_should_give_setups_super_call_when_in_describes(self):
        test = '''
        describe "Thing":
            before_each:
                self.x = 5
        '''
        
        desired = '''
        class TestThing (object ):
            def setUp (self ):
                noy_sup_setUp (super (TestThing ,self ));self .x =5 
        '''
        
        (self.toka, test) |should| result_in(desired)
        # and with tabs
        (self.toka, test.replace('    ', '\t')) |should| result_in(desired.replace('    ', '\t'))
        
    def test_it_should_turn_after_each_into_teardown(self):
        (self.toka, 'after_each:') |should| result_in('def tearDown (self ):')
        
        # Same tests, but with newlines in front
        (self.toka, '\nafter_each:') |should| result_in('\ndef tearDown (self ):')
    
    def test_it_should_give_teardowns_super_call_when_in_describes(self):
        test = '''
        describe "Thing":
            after_each:
                self.x = 5
        '''
        
        desired = '''
        class TestThing (object ):
            def tearDown (self ):
                noy_sup_tearDown (super (TestThing ,self ));self .x =5 
        '''
        
        (self.toka, test) |should| result_in(desired)
        # and with tabs
        (self.toka, test.replace('    ', '\t')) |should| result_in(desired.replace('    ', '\t'))
    
    def test_it_should_have_ignorable_its(self):
        (self.toka, '\nignore "should be ignored"') |should| result_in(
            '\ndef ignore__should_be_ignored ():raise nose.SkipTest '
            )
        (self.toka, '\nignore "should be ignored"') |should| result_in(
            '\ndef ignore__should_be_ignored ():raise nose.SkipTest '
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
        class TestAnotherThing (%s ):pass 
        '''
        
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
        def test_root_level_should_work_well ():raise nose.SkipTest 
            3 |should |be (4 )
        class TestSomeTests (%s ):
            def test_doesnt_get_phased_by_special_characters (self ):raise nose.SkipTest 

        class TestSomeTests_NestedDescribe (TestSomeTests ):
            def test_asdf_asdf (self ):
                1 |should |be (2 )
        def test_root_level_should_also_work ():raise nose.SkipTest 
        test_root_level_should_work_well .__testname__ ="(root level) should work {well}"
        test_root_level_should_also_work .__testname__ ="(root level) should also [work]"
        TestSomeTests .test_doesnt_get_phased_by_special_characters .__func__ .__testname__ ="doesn't get phased by $special characters"
        TestSomeTests_NestedDescribe .test_asdf_asdf .__func__ .__testname__ ="asdf $%% asdf"
        '''
        
        (self.toka, test) |should| result_in(desired % "object")
        (self.tokb, test) |should| result_in(desired % "other")
    
    def test_it_maintains_line_numbers_when_pass_on_another_line(self):
        test = '''
        it "is a function with a pass": pass
        
        it "is a function with a pass on another line":
            pass
        
        it "is a function with a pass on another line further below":
            #comment or something
            
            
            pass
        
        describe "block with a pass":
            pass
        
        describe "block with comment and pass":
            # comment or something
            pass
        
        describe "Nesting and passes": pass
            # comment
            describe "Nested":
                pass
                
                describe "More Nesting":
                    # comment
                    
                    
                    pass
        '''
        
        desired = '''
        def test_is_a_function_with_a_pass ():pass 

        def test_is_a_function_with_a_pass_on_another_line ():
            pass 

        def test_is_a_function_with_a_pass_on_another_line_further_below ():
        #comment or something
            
            
            pass 

        class TestBlockWithAPass (%(dflt)s ):
            pass 

        class TestBlockWithCommentAndPass (%(dflt)s ):
        # comment or something
            pass 

        class TestNestingAndPasses (%(dflt)s ):pass 
        # comment
        class TestNestingAndPasses_Nested (TestNestingAndPasses ):
            pass 

        class TestNestingAndPasses_Nested_MoreNesting (TestNestingAndPasses_Nested ):
        # comment
        
        
            pass
        '''
        
        (self.toka, test) |should| result_in(desired % {'dflt': "object"})
        (self.tokb, test) |should| result_in(desired % {'dflt': "other"})
    
    def test_it_allows_default_arguments_for_its(self):
        test = '''
        it "is a test with default arguments", thing=2, other=[3]
        
        describe "group":
            it "has self and default args", blah=None, you=(3, 4,
                5, 5):
                # Test space is respected
                
                1 |should| be(2)
        '''
        
        desired = '''
        def test_is_a_test_with_default_arguments (thing =2 ,other =[3 ]):raise nose.SkipTest 

        class TestGroup (%(dflt)s ):
            def test_has_self_and_default_args (self ,blah =None ,you =(3 ,4 ,
            5 ,5 )):
            # Test space is respected
                
                1 |should |be (2 )
        '''
        
        (self.toka, test) |should| result_in(desired % {'dflt': "object"})
        (self.tokb, test) |should| result_in(desired % {'dflt': "other"})