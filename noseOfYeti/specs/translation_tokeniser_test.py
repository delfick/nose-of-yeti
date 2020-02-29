from noseOfYeti.tokeniser import Tokeniser
from should_dsl import should

from unittest import TestCase

# Silencing code checker about should_dsl matchers
result_in = None


class Test_Tokenisor_translation(TestCase):
    def setUp(self):
        self.toka = Tokeniser(with_describe_attrs=False)

    def test_translates_a_describe(self):
        (self.toka, 'describe "Something testable"') | should | result_in(
            "class TestSomethingTestable ():pass"
        )

        # Same tests, but with newlines in front
        (self.toka, '\ndescribe "Something testable"') | should | result_in(
            "\nclass TestSomethingTestable ():pass"
        )

    def test_translates_an_it(self):
        (self.toka, 'it "should do this thing":') | should | result_in(
            "def test_should_do_this_thing ():"
        )

        # Same tests, but with newlines in front
        (self.toka, '\nit "should do this thing":') | should | result_in(
            "\ndef test_should_do_this_thing ():"
        )

        ## and with async

        (self.toka, 'async it "should do this thing":') | should | result_in(
            "async def test_should_do_this_thing ():"
        )

        # Same tests, but with newlines in front
        (self.toka, '\nasync it "should do this thing":') | should | result_in(
            "\nasync def test_should_do_this_thing ():"
        )

    def test_adds_arguments_to_its_if_declared_on_same_line(self):
        (self.toka, 'it "should do this thing", blah, meh:') | should | result_in(
            "def test_should_do_this_thing (blah ,meh ):"
        )

        # Same tests, but with newlines in front
        (self.toka, '\nit "should do this thing", blah, meh:') | should | result_in(
            "\ndef test_should_do_this_thing (blah ,meh ):"
        )

    def test_adds_arguments_to_its_if_declared_on_same_line_and_work_with_skipTest(self):
        (self.toka, 'it "should do this thing", blah, meh: pass') | should | result_in(
            "def test_should_do_this_thing (blah ,meh ):pass"
        )

        # Same tests, but with newlines in front
        (self.toka, '\nit "should do this thing", blah, meh:\n    pass') | should | result_in(
            "\ndef test_should_do_this_thing (blah ,meh ):\n    pass"
        )

    def test_complains_about_it_that_isnt_a_block(self):
        with self.assertRaisesRegex(SyntaxError, "Found a missing ':' on line 1, column 22"):
            (self.toka, 'it "should be skipped"\n') | should | result_in("")

        # Same tests, but with newlines in front
        with self.assertRaisesRegex(SyntaxError, "Found a missing ':' on line 3, column 22"):
            (self.toka, 'import os\n\nit "should be skipped"\n') | should | result_in("")

        (self.toka, 'import os\n\nit "should not be skipped":\n') | should | result_in(
            "import os\n\ndef test_should_not_be_skipped ():"
        )

        ## And with async

        with self.assertRaises(SyntaxError, msg="Found a missing ':' on line 1, column 28"):
            (self.toka, 'async it "should be skipped"\n') | should | result_in("")

        (self.toka, 'async it "should not be skipped":\n') | should | result_in(
            "async def test_should_not_be_skipped ():"
        )

        # Same tests, but with newlines in front
        with self.assertRaises(SyntaxError, msg="Found a missing ':' on line 2, column 28"):
            (self.toka, 'import os\nasync it "should be skipped"\n') | should | result_in("")

        (self.toka, 'import os\nasync it "should not be skipped":\n') | should | result_in(
            "import os\nasync def test_should_not_be_skipped ():"
        )

    def test_turns_before_each_into_setup(self):
        (self.toka, "before_each:") | should | result_in("def setUp (self ):")

        # Same tests, but with newlines in front
        (self.toka, "\nbefore_each:") | should | result_in("\ndef setUp (self ):")

        # And with async
        (self.toka, "async before_each:") | should | result_in("async def setUp (self ):")

        # Same tests, but with newlines in front
        (self.toka, "\nasync before_each:") | should | result_in("\nasync def setUp (self ):")

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
            it 'asdf2':
                pass"""

        desired = """
        class TestA ():
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
            def test_asdf2 (self ):
                pass
        """

        (self.toka, test) | should | result_in(desired)

    def test_complains_if_describe_after_hanging_it(self):
        test = """
        describe 'thing':
            it 'should be skipped'
            describe 'that':
                pass"""

        with self.assertRaisesRegex(SyntaxError, "Found a missing ':' on line 2, column 26"):
            (self.toka, test) | should | result_in("")

    def test_indentation_should_work_for_inline_python_code(self):
        test = """
        describe 'this':
            describe 'that':
                pass

        class SomeMockObject():
            def indented_method()
        """

        desired = """
        class TestThis ():pass
        class TestThis_That (TestThis ):
            pass

        class SomeMockObject ():
            def indented_method ()
        """

        (self.toka, test) | should | result_in(desired)

    def test_gives_setups_super_call_when_in_describes_that_know_about_await_if_async(self):
        test = """
        describe "Thing":
            async before_each:
                self.x = 5
        """

        desired = """
        class TestThing ():
            async def setUp (self ):
                await async_noy_sup_setUp (super (TestThing ,self ));self .x =5
        """

        (self.toka, test) | should | result_in(desired)
        # and with tabs
        (self.toka, test.replace("    ", "\t")) | should | result_in(desired.replace("    ", "\t"))

    def test_gives_setups_super_call_when_in_describes(self):
        test = """
        describe "Thing":
            before_each:
                self.x = 5
        """

        desired = """
        class TestThing ():
            def setUp (self ):
                noy_sup_setUp (super (TestThing ,self ));self .x =5
        """

        (self.toka, test) | should | result_in(desired)
        # and with tabs
        (self.toka, test.replace("    ", "\t")) | should | result_in(desired.replace("    ", "\t"))

    def test_turns_after_each_into_teardown(self):
        (self.toka, "after_each:") | should | result_in("def tearDown (self ):")

        # Same tests, but with newlines in front
        (self.toka, "\nafter_each:") | should | result_in("\ndef tearDown (self ):")

    def test_gives_teardowns_super_call_that_awaits_when_in_describes_and_async(self):
        test = """
        describe "Thing":
            async after_each:
                self.x = 5
        """

        desired = """
        class TestThing ():
            async def tearDown (self ):
                await async_noy_sup_tearDown (super (TestThing ,self ));self .x =5
        """

        (self.toka, test) | should | result_in(desired)
        # and with tabs
        (self.toka, test.replace("    ", "\t")) | should | result_in(desired.replace("    ", "\t"))

    def test_gives_teardowns_super_call_when_in_describes(self):
        test = """
        describe "Thing":
            after_each:
                self.x = 5
        """

        desired = """
        class TestThing ():
            def tearDown (self ):
                noy_sup_tearDown (super (TestThing ,self ));self .x =5
        """

        (self.toka, test) | should | result_in(desired)
        # and with tabs
        (self.toka, test.replace("    ", "\t")) | should | result_in(desired.replace("    ", "\t"))

    def test_no_transform_inside_expression(self):
        (self.toka, "variable = before_each") | should | result_in("variable =before_each ")
        (self.toka, "variable = after_each") | should | result_in("variable =after_each ")
        (self.toka, "variable = describe") | should | result_in("variable =describe ")
        (self.toka, "variable = ignore") | should | result_in("variable =ignore ")
        (self.toka, "variable = it") | should | result_in("variable =it ")

        # Same tests, but with newlines in front
        (self.toka, "\nvariable = before_each") | should | result_in("\nvariable =before_each ")
        (self.toka, "\nvariable = after_each") | should | result_in("\nvariable =after_each ")
        (self.toka, "\nvariable = describe") | should | result_in("\nvariable =describe ")
        (self.toka, "\nvariable = ignore") | should | result_in("\nvariable =ignore ")
        (self.toka, "\nvariable = it") | should | result_in("\nvariable =it ")

    def test_sets__testname__on_non_alphanumeric_test_names(self):
        test = """
        it "(root level) should work {well}":
            3 |should| be(4)
        describe "SomeTests":
            it "doesn't get phased by $special characters":
                pass

            describe "NestedDescribe":
                it "asdf $% asdf":
                    1 |should| be(2)
        """

        desired = """
        def test_root_level_should_work_well ():
            3 |should |be (4 )
        class TestSomeTests ():
            def test_doesnt_get_phased_by_special_characters (self ):
                pass

        class TestSomeTests_NestedDescribe (TestSomeTests ):
            def test_asdf_asdf (self ):
                1 |should |be (2 )
        test_root_level_should_work_well .__testname__ ="(root level) should work {well}"
        TestSomeTests .test_doesnt_get_phased_by_special_characters .__testname__ ="doesn't get phased by $special characters"
        TestSomeTests_NestedDescribe .test_asdf_asdf .__testname__ ="asdf $% asdf"
        """

        (self.toka, test) | should | result_in(desired)

    def test_it_maintains_line_numbers_when_pass_on_another_line(self):
        test = """
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
        """

        desired = """
        def test_is_a_function_with_a_pass ():pass

        def test_is_a_function_with_a_pass_on_another_line ():
            pass

        def test_is_a_function_with_a_pass_on_another_line_further_below ():
        #comment or something


            pass

        class TestBlockWithAPass ():
            pass

        class TestBlockWithCommentAndPass ():
        # comment or something
            pass

        class TestNestingAndPasses ():pass
        # comment
        class TestNestingAndPasses_Nested (TestNestingAndPasses ):
            pass

        class TestNestingAndPasses_Nested_MoreNesting (TestNestingAndPasses_Nested ):
        # comment


            pass
        """

        (self.toka, test) | should | result_in(desired)

    def test_it_allows_default_arguments_for_its(self):
        test = """
        it "is a test with default arguments", thing=2, other=[3]:
            pass

        describe "group":
            it "has self and default args", blah=None, you=(3, 4,
                5, 5):
                # Test space is respected

                1 |should| be(2)
        """

        desired = """
        def test_is_a_test_with_default_arguments (thing =2 ,other =[3 ]):
            pass

        class TestGroup ():
            def test_has_self_and_default_args (self ,blah =None ,you =(3 ,4 ,
            5 ,5 )):
            # Test space is respected

                1 |should |be (2 )
        """

        (self.toka, test) | should | result_in(desired)

    def test_can_properly_dedent_after_block_of_just_containers(self):
        test = """
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
        """

        desired = """
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
        """

        (self.toka, test) | should | result_in(desired)

    def test_it_doesnt_add_semicolon_after_noy_setup_if_not_necessary(self):
        test = """
            describe "block with necessary semicolon":
                before_each:
                    two = 1 + 1

            describe "block with unecessary semiclon":
                before_each:
                    #comment
                    pass

                after_each:

                    pass
        """

        desired = """
        class TestBlockWithNecessarySemicolon ():
            def setUp (self ):
                noy_sup_setUp (super (TestBlockWithNecessarySemicolon ,self ));two =1 +1

        class TestBlockWithUnecessarySemiclon ():
            def setUp (self ):
                noy_sup_setUp (super (TestBlockWithUnecessarySemiclon ,self ))#comment
                pass

            def tearDown (self ):
                noy_sup_tearDown (super (TestBlockWithUnecessarySemiclon ,self ))
                pass
        """
        (self.toka, test) | should | result_in(desired)

    def test_it_keeps_comments_placed_after_setup_and_teardown_methods(self):
        test = """
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
        """

        desired = """
        class TestKls ():
            def setUp (self ):# Comment one
                noy_sup_setUp (super (TestKls ,self ))
                pass

            def tearDown (self ):# Comment two
                noy_sup_tearDown (super (TestKls ,self ))
                pass

        class TestKls2 ():
            def setUp (self ):# Comment three
                noy_sup_setUp (super (TestKls2 ,self ));two =1 +1

            def tearDown (self ):# Comment four
                noy_sup_tearDown (super (TestKls2 ,self ))#comment
                pass
        """
        (self.toka, test) | should | result_in(desired)
