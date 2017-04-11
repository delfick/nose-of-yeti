from noseOfYeti.tokeniser import Tokeniser
from should_dsl import should

import six

# Silencing code checker about should_dsl matchers
result_in = None

func_accessor = ""
if six.PY2:
    func_accessor = "__func__ ."

class Test_Tokenisor_translation(object):
    def setUp(self):
        self.toka = Tokeniser(with_describe_attrs=False)
        self.tokb = Tokeniser(with_describe_attrs=False, default_kls = 'other')

    def test_translates_a_describe(self):
        (self.toka, 'describe "Something testable"') |should| result_in('class TestSomethingTestable (object ):pass')
        (self.tokb, 'describe "Something testable"') |should| result_in('class TestSomethingTestable (other ):pass')

        # Same tests, but with newlines in front
        (self.toka, '\ndescribe "Something testable"') |should| result_in('\nclass TestSomethingTestable (object ):pass')
        (self.tokb, '\ndescribe "Something testable"') |should| result_in('\nclass TestSomethingTestable (other ):pass')

    def test_translates_an_it(self):
        (self.toka, 'it "should do this thing":') |should| result_in('def test_should_do_this_thing ():')
        (self.tokb, 'it "should do this thing":') |should| result_in('def test_should_do_this_thing ():')

        # Same tests, but with newlines in front
        (self.toka, '\nit "should do this thing":') |should| result_in('\ndef test_should_do_this_thing ():')
        (self.tokb, '\nit "should do this thing":') |should| result_in('\ndef test_should_do_this_thing ():')

        ## and with async

        (self.toka, 'async it "should do this thing":') |should| result_in('async def test_should_do_this_thing ():')
        (self.tokb, 'async it "should do this thing":') |should| result_in('async def test_should_do_this_thing ():')

        # Same tests, but with newlines in front
        (self.toka, '\nasync it "should do this thing":') |should| result_in('\nasync def test_should_do_this_thing ():')
        (self.tokb, '\nasync it "should do this thing":') |should| result_in('\nasync def test_should_do_this_thing ():')

    def test_adds_arguments_to_its_if_declared_on_same_line(self):
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

    def test_adds_arguments_to_its_if_declared_on_same_line_and_work_with_skipTest(self):
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

    def test_no_added_arguments_to_its_if_not_declared_on_same_line(self):
        (self.toka, 'it "should do this thing"\n, blah, meh') |should| result_in(
            "def test_should_do_this_thing ():raise nose.SkipTest\n,blah ,meh "
            )
        (self.tokb, 'it "should do this thing"\n, blah, meh') |should| result_in(
            "def test_should_do_this_thing ():raise nose.SkipTest\n,blah ,meh "
            )

        # Same tests, but with newlines in front
        (self.toka, '\nit "should do this thing"\n, blah, meh') |should| result_in(
            "\ndef test_should_do_this_thing ():raise nose.SkipTest\n,blah ,meh "
            )
        (self.tokb, '\nit "should do this thing"\n, blah, meh') |should| result_in(
            "\ndef test_should_do_this_thing ():raise nose.SkipTest\n,blah ,meh "
            )

    def test_turns_an_it_without_colon_into_skippable(self):
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


        ## And with async

        (self.toka, 'async it "should be skipped"\n') |should| result_in(
            'async def test_should_be_skipped ():raise nose.SkipTest '
        )

        (self.toka, 'async it "should not be skipped":\n') |should| result_in(
            'async def test_should_not_be_skipped ():'
        )

        # Same tests, but with newlines in front
        (self.toka, '\nasync it "should be skipped"\n') |should| result_in(
            '\nasync def test_should_be_skipped ():raise nose.SkipTest '
        )

        (self.toka, '\nasync it "should not be skipped":\n') |should| result_in(
            '\nasync def test_should_not_be_skipped ():'
        )

    def test_turns_before_each_into_setup(self):
        (self.toka, 'before_each:') |should| result_in('def setUp (self ):')

        # Same tests, but with newlines in front
        (self.toka, '\nbefore_each:') |should| result_in('\ndef setUp (self ):')

        # And with async
        (self.toka, 'async before_each:') |should| result_in('async def setUp (self ):')

        # Same tests, but with newlines in front
        (self.toka, '\nasync before_each:') |should| result_in('\nasync def setUp (self ):')

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

    def test_gives_setups_super_call_when_in_describes_that_know_about_await_if_async(self):
        test = '''
        describe "Thing":
            async before_each:
                self.x = 5
        '''

        desired = '''
        class TestThing (object ):
            async def setUp (self ):
                await async_noy_sup_setUp (super (TestThing ,self ));self .x =5
        '''

        (self.toka, test) |should| result_in(desired)
        # and with tabs
        (self.toka, test.replace('    ', '\t')) |should| result_in(desired.replace('    ', '\t'))

    def test_gives_setups_super_call_when_in_describes(self):
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

    def test_turns_after_each_into_teardown(self):
        (self.toka, 'after_each:') |should| result_in('def tearDown (self ):')

        # Same tests, but with newlines in front
        (self.toka, '\nafter_each:') |should| result_in('\ndef tearDown (self ):')

    def test_gives_teardowns_super_call_that_awaits_when_in_describes_and_async(self):
        test = '''
        describe "Thing":
            async after_each:
                self.x = 5
        '''

        desired = '''
        class TestThing (object ):
            async def tearDown (self ):
                await async_noy_sup_tearDown (super (TestThing ,self ));self .x =5
        '''

        (self.toka, test) |should| result_in(desired)
        # and with tabs
        (self.toka, test.replace('    ', '\t')) |should| result_in(desired.replace('    ', '\t'))

    def test_gives_teardowns_super_call_when_in_describes(self):
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

    def test_it_has_the_ability_to_wrap_async_setup_and_tearDown_instead_of_inserting_sup_call(self):
        self.toka.wrapped_setup = True
        self.tokb.wrapped_setup = True

        test = '''
        describe "Thing":
            async after_each:
                self.x = 5

            describe "Other":
                async before_each:
                    self.y = 8
        '''

        desired = '''
        class TestThing (object ):
            async def tearDown (self ):
                self .x =5

        class TestThing_Other (TestThing ):
            async def setUp (self ):
                self .y =8

        TestThing .tearDown =async_noy_wrap_tearDown (TestThing ,TestThing .tearDown )
        TestThing_Other .setUp =async_noy_wrap_setUp (TestThing_Other ,TestThing_Other .setUp )
        '''

        (self.toka, test) |should| result_in(desired)
        (self.toka, test.replace('    ', '\t')) |should| result_in(desired.replace('    ', '\t'))

    def test_it_has_the_ability_to_wrap_setup_and_tearDown_instead_of_inserting_sup_call(self):
        self.toka.wrapped_setup = True
        self.tokb.wrapped_setup = True

        test = '''
        describe "Thing":
            after_each:
                self.x = 5

            describe "Other":
                before_each:
                    self.y = 8
        '''

        desired = '''
        class TestThing (object ):
            def tearDown (self ):
                self .x =5

        class TestThing_Other (TestThing ):
            def setUp (self ):
                self .y =8

        TestThing .tearDown =noy_wrap_tearDown (TestThing ,TestThing .tearDown )
        TestThing_Other .setUp =noy_wrap_setUp (TestThing_Other ,TestThing_Other .setUp )
        '''

        (self.toka, test) |should| result_in(desired)
        (self.toka, test.replace('    ', '\t')) |should| result_in(desired.replace('    ', '\t'))

    def test_it_is_possible_to_have_indented_block_after_setup_with_wrapped_setup_option(self):
        self.toka.wrapped_setup = True
        self.tokb.wrapped_setup = True

        test = '''
        describe "Thing":
            after_each:
                def blah(self):
                    pass

            describe "Other":
                before_each:
                    class Stuff(object):
                        pass
        '''

        desired = '''
        class TestThing (object ):
            def tearDown (self ):
                def blah (self ):
                    pass

        class TestThing_Other (TestThing ):
            def setUp (self ):
                class Stuff (object ):
                    pass

        TestThing .tearDown =noy_wrap_tearDown (TestThing ,TestThing .tearDown )
        TestThing_Other .setUp =noy_wrap_setUp (TestThing_Other ,TestThing_Other .setUp )
        '''

        (self.toka, test) |should| result_in(desired)
        (self.toka, test.replace('    ', '\t')) |should| result_in(desired.replace('    ', '\t'))


    def test_has_ignorable_its(self):
        (self.toka, '\nignore "should be ignored"') |should| result_in(
            '\ndef ignore__should_be_ignored ():raise nose.SkipTest '
            )
        (self.toka, '\nignore "should be ignored"') |should| result_in(
            '\ndef ignore__should_be_ignored ():raise nose.SkipTest '
            )
        (self.toka, '\nasync ignore "should be ignored"') |should| result_in(
            '\nasync def ignore__should_be_ignored ():raise nose.SkipTest '
            )

    def test_no_transform_inside_expression(self):
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

    def test_allows_definition_of_different_base_class_for_next_describe(self):
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

    def test_sets__testname__on_non_alphanumeric_test_names(self):
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
        test_root_level_should_work_well .__testname__ ="(root level) should work {{well}}"
        test_root_level_should_also_work .__testname__ ="(root level) should also [work]"
        TestSomeTests .test_doesnt_get_phased_by_special_characters .{func_accessor}__testname__ ="doesn't get phased by $special characters"
        TestSomeTests_NestedDescribe .test_asdf_asdf .{func_accessor}__testname__ ="asdf $%% asdf"
        '''.format(func_accessor=func_accessor)

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

    def test_can_properly_dedent_after_block_of_just_containers(self):
        test = '''
        it "should ensure askers are None or boolean or string":
            for val in (None, False, 'asdf', u'asdf', lambda: 1):
                (lambda : Step(askBeforeAction  = val)) |should_not| throw(Problem)
                (lambda : Step(askDesiredResult = val)) |should_not| throw(Problem)
                (lambda : Step(blockBeforeGet   = val)) |should_not| throw(Problem)

            for val in (1, True):
                (lambda : Step(askBeforeAction  = val)) |should| throw(Problem)
                (lambda : Step(askDesiredResult = val)) |should| throw(Problem)
                (lambda : Step(blockBeforeGet   = val)) |should| throw(Problem)

            3 |should| be(3)
        '''

        desired = '''
        def test_should_ensure_askers_are_None_or_boolean_or_string ():
            for val in (None ,False ,'asdf',u'asdf',lambda :1 ):
                (lambda :Step (askBeforeAction =val ))|should_not |throw (Problem )
                (lambda :Step (askDesiredResult =val ))|should_not |throw (Problem )
                (lambda :Step (blockBeforeGet =val ))|should_not |throw (Problem )

            for val in (1 ,True ):
                (lambda :Step (askBeforeAction =val ))|should |throw (Problem )
                (lambda :Step (askDesiredResult =val ))|should |throw (Problem )
                (lambda :Step (blockBeforeGet =val ))|should |throw (Problem )

            3 |should |be (3 )
        '''

        (self.toka, test) |should| result_in(desired)
        (self.tokb, test) |should| result_in(desired)

    def test_it_doesnt_add_semicolon_after_noy_setup_if_not_necessary(self):
        test = '''
            describe "block with necessary semicolon":
                before_each:
                    two = 1 + 1

            describe "block with unecessary semiclon":
                before_each:
                    #comment
                    pass

                after_each:

                    pass
        '''

        desired = '''
        class TestBlockWithNecessarySemicolon (%(dflt)s ):
            def setUp (self ):
                noy_sup_setUp (super (TestBlockWithNecessarySemicolon ,self ));two =1 +1

        class TestBlockWithUnecessarySemiclon (%(dflt)s ):
            def setUp (self ):
                noy_sup_setUp (super (TestBlockWithUnecessarySemiclon ,self ))#comment
                pass

            def tearDown (self ):
                noy_sup_tearDown (super (TestBlockWithUnecessarySemiclon ,self ))
                pass
        '''
        (self.toka, test) |should| result_in(desired % {'dflt': "object"})
        (self.tokb, test) |should| result_in(desired % {'dflt': "other"})

    def test_it_keeps_comments_placed_after_setup_and_teardown_methods(self):
        test = '''
            describe "Kls":
                before_each: # Comment one

                    pass

                after_each: # Comment two

                    pass

            describe "Kls2":
                before_each: # Comment three
                    two = 1 + 1

                after_each: # Comment four
                    #comment
                    pass
        '''

        desired = '''
        class TestKls (%(dflt)s ):
            def setUp (self ):# Comment one
                noy_sup_setUp (super (TestKls ,self ))
                pass

            def tearDown (self ):# Comment two
                noy_sup_tearDown (super (TestKls ,self ))
                pass

        class TestKls2 (%(dflt)s ):
            def setUp (self ):# Comment three
                noy_sup_setUp (super (TestKls2 ,self ));two =1 +1

            def tearDown (self ):# Comment four
                noy_sup_tearDown (super (TestKls2 ,self ))#comment
                pass
        '''
        (self.toka, test) |should| result_in(desired % {'dflt': "object"})
        (self.tokb, test) |should| result_in(desired % {'dflt': "other"})

