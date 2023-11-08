import sys
from textwrap import dedent

import pytest


def assert_example(original, desired):
    tab_original = original.replace("    ", "\t")
    tab_desired = desired.replace("    ", "\t")

    options = {"with_describe_attrs": False}

    for original, desired in ((original, desired), (tab_original, tab_desired)):
        pytest.helpers.assert_conversion(original, desired, tokeniser=options)

        # And with newlines
        original = f"import os\n{dedent(original)}"
        desired = f"import os\n{dedent(desired)}"
        pytest.helpers.assert_conversion(original, desired, tokeniser=options)


class Test_Tokenisor_translation:
    def test_translates_a_describe(self):
        original = 'describe "Something testable"'
        desired = "class TestSomethingTestable :pass"
        assert_example(original, desired)

    def test_translates_an_it(self):
        original = 'it "should do this thing":'
        desired = "def test_should_do_this_thing ()$RET:"
        assert_example(original, desired)

        ## and with async
        original = 'async it "should do this thing":'
        desired = "async def test_should_do_this_thing ()$RET:"
        assert_example(original, desired)

    def test_translates_an_it_with_return_type(self):
        original = 'it "should do this thing" -> None:'
        desired = "def test_should_do_this_thing ()->None :"
        assert_example(original, desired)

        ## and with async
        original = 'async it "should do this thing" -> None:'
        desired = "async def test_should_do_this_thing ()->None :"
        assert_example(original, desired)

    def test_translates_an_it_with_complex_return_type(self):
        original = 'it "should do this thing" -> tp.Generic[Thing, list[str]]:'
        desired = "def test_should_do_this_thing ()->tp .Generic [Thing list [str ]]:"
        assert_example(original, desired)

        ## and with async
        original = 'async it "should do this thing" -> tp.Generic[Thing, list[str]]:'
        desired = "async def test_should_do_this_thing ()->tp .Generic [Thing list [str ]]:"
        assert_example(original, desired)

    def test_translates_an_it_with_return_type_and_args(self):
        original = 'it "should do this thing", one: str -> None:'
        desired = "def test_should_do_this_thing (one :str )->None :"
        assert_example(original, desired)

        ## and with async
        original = 'async it "should do this thing", two: int -> None:'
        desired = "async def test_should_do_this_thing (two :int )->None :"
        assert_example(original, desired)

    def test_translates_an_it_with_complex_return_type_and_args(self):
        original = (
            'it "should do this thing" blah: dict[str, list] -> tp.Generic[Thing, list[str]]:'
        )
        desired = "def test_should_do_this_thing (blah :dict [str ,list ])->tp .Generic [Thing ,list [str ]]:"
        assert_example(original, desired)

        ## and with async
        original = 'async it "should do this thing" item: Item -> tp.Generic[Thing, list[str]]:'
        desired = (
            "async def test_should_do_this_thing (item :Item )->tp .Generic [Thing ,list [str ]]:"
        )
        assert_example(original, desired)

    def test_adds_arguments_to_its_if_declared_on_same_line(self):
        original = 'it "should do this thing", blah, meh:'
        desired = "def test_should_do_this_thing (blah ,meh )$RET:"
        assert_example(original, desired)

    def test_adds_arguments_with_default_string_to_its_if_declared_on_same_line(self):
        original = 'it "should do this thing", blah, meh="hello":'
        desired = 'def test_should_do_this_thing (blah ,meh ="hello")$RET:'
        assert_example(original, desired)

    def test_adds_type_annotations(self):
        original = 'it "should do this thing", blah:str, meh: Thing | Other:'
        desired = "def test_should_do_this_thing (blah :str ,meh :Thing |Other )$RET:"
        assert_example(original, desired)

    def test_allows_comments_after_it(self):
        original = 'it "should do this thing", blah:str, meh: Thing | Other: # a comment'
        desired = "def test_should_do_this_thing (blah :str ,meh :Thing |Other )$RET:# a comment"
        assert_example(original, desired)

        original = 'it "should do this thing":  # a comment'
        desired = "def test_should_do_this_thing ()$RET:# a comment"
        assert_example(original, desired)

    def test_adds_arguments_to_its_if_declared_on_same_line_and_work_with_skipTest(self):
        original = 'it "should do this thing", blah, meh: pass'
        desired = "def test_should_do_this_thing (blah ,meh )$RET:pass"
        assert_example(original, desired)

    def test_complains_about_it_that_isnt_a_block(self):
        with pytest.raises(SyntaxError, match="Found a missing ':' on line 1, column 22"):
            assert_example('it "should be skipped"\n', "")

        with pytest.raises(SyntaxError, match="Found a missing ':' on line 1, column 22"):
            assert_example('it "should be skipped" # blah\n', "")

        # Same tests, but with newlines in front
        with pytest.raises(SyntaxError, match="Found a missing ':' on line 3, column 22"):
            assert_example('import os\n\nit "should be skipped"\n', "")

        original = 'import os\n\nit "should not be skipped":\n'
        desired = "import os\n\ndef test_should_not_be_skipped ()$RET:"
        assert_example(original, desired)

        ## And with async

        with pytest.raises(SyntaxError, match="Found a missing ':' on line 1, column 28"):
            assert_example('async it "should be skipped"\n', "")

        original = 'import os\n\nasync it "should not be skipped":\n'
        desired = "import os\n\nasync def test_should_not_be_skipped ()$RET:"
        assert_example(original, desired)

        # Same tests, but with newlines in front
        with pytest.raises(SyntaxError, match="Found a missing ':' on line 3, column 28"):
            assert_example('import os\n\nasync it "should be skipped"\n', "")

        original = 'import os\n\nasync it "should not be skipped":\n'
        desired = "import os\n\nasync def test_should_not_be_skipped ()$RET:"
        assert_example(original, desired)

    def test_turns_before_each_into_setup(self):
        assert_example("before_each:", "def setUp (self ):")

        # And with async
        assert_example("async before_each:", "async def setUp (self ):")

    def test_indentation_should_work_regardless_of_crazy_groups(self):
        original = """
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
        class TestA :
            def test_asdf (self )$RET:
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
            def test_asdf2 (self )$RET:
                pass
        """

        assert_example(original, desired)

    def test_complains_if_describe_after_hanging_it(self):
        original = """
        describe 'thing':
            it 'should be skipped'
            describe 'that':
                pass
        """

        with pytest.raises(SyntaxError, match="Found a missing ':' on line 2, column 26"):
            assert_example(original, "")

    def test_indentation_should_work_for_inline_python_code(self):
        original = """
        describe 'this':
            describe 'that':
                pass

        class SomeMockObject:
            def indented_method()
        """

        desired = """
        class TestThis :pass
        class TestThis_That (TestThis ):
            pass

        class SomeMockObject :
            def indented_method ()
        """

        assert_example(original, desired)

    def test_gives_setups_super_call_when_in_describes_that_know_about_await_if_async(self):
        original = """
        describe "Thing":
            async before_each:
                self.x = 5
        """

        desired = """
        class TestThing :
            async def setUp (self ):
                await __import__ ("noseOfYeti").tokeniser .TestSetup (super ()).async_before_each ();self .x =5
        """

        assert_example(original, desired)

    def test_gives_setups_super_call_when_in_describes(self):
        original = """
        describe "Thing":
            before_each:
                self.x = 5
        """

        desired = """
        class TestThing :
            def setUp (self ):
                __import__ ("noseOfYeti").tokeniser .TestSetup (super ()).sync_before_each ();self .x =5
        """

        assert_example(original, desired)

    def test_turns_after_each_into_teardown(self):
        assert_example("after_each:", "def tearDown (self ):")

    def test_gives_teardowns_super_call_that_awaits_when_in_describes_and_async(self):
        original = """
        describe "Thing":
            async after_each:
                self.x = 5
        """

        desired = """
        class TestThing :
            async def tearDown (self ):
                await __import__ ("noseOfYeti").tokeniser .TestSetup (super ()).async_after_each ();self .x =5
        """

        assert_example(original, desired)

    def test_gives_teardowns_super_call_when_in_describes(self):
        original = """
        describe "Thing":
            after_each:
                self.x = 5
        """

        desired = """
        class TestThing :
            def tearDown (self ):
                __import__ ("noseOfYeti").tokeniser .TestSetup (super ()).sync_after_each ();self .x =5
        """

        assert_example(original, desired)

    def test_no_transform_inside_expression(self):
        assert_example("variable = before_each", "variable =before_each ")
        assert_example("variable = after_each", "variable =after_each ")
        assert_example("variable = describe", "variable =describe ")
        assert_example("variable = ignore", "variable =ignore ")
        assert_example("variable = it", "variable =it ")

    def test_sets__testname__on_non_alphanumeric_test_names(self):
        original = """
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
        def test_root_level_should_work_well ()$RET:
            3 |should |be (4 )
        class TestSomeTests :
            def test_doesnt_get_phased_by_special_characters (self )$RET:
                pass

        class TestSomeTests_NestedDescribe (TestSomeTests ):
            def test_asdf_asdf (self )$RET:
                1 |should |be (2 )

        test_root_level_should_work_well .__testname__ ="(root level) should work {well}"  # type: ignore
        TestSomeTests .test_doesnt_get_phased_by_special_characters .__testname__ ="doesn't get phased by $special characters"  # type: ignore
        TestSomeTests_NestedDescribe .test_asdf_asdf .__testname__ ="asdf $% asdf"  # type: ignore
        """

        assert_example(original, desired)

    def test_it_maintains_line_numbers_when_pass_on_another_line(self):
        original = """
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
        def test_is_a_function_with_a_pass ()$RET:pass

        def test_is_a_function_with_a_pass_on_another_line ()$RET:
            pass

        def test_is_a_function_with_a_pass_on_another_line_further_below ()$RET:
            #comment or something


            pass

        class TestBlockWithAPass :
            pass

        class TestBlockWithCommentAndPass :
            # comment or something
            pass

        class TestNestingAndPasses :pass
            # comment
        class TestNestingAndPasses_Nested (TestNestingAndPasses ):
            pass

        class TestNestingAndPasses_Nested_MoreNesting (TestNestingAndPasses_Nested ):
            # comment


            pass
        """

        assert_example(original, desired)

    def test_it_allows_default_arguments_for_its(self):
        original = """
        it "is a test with default arguments", thing=2, other=[3]:
            pass

        describe "group":
            it "has self and default args", blah=None, you=(3, 4,
                5, 5):
                # Test space is respected

                1 |should| be(2)
        """

        desired = """
        def test_is_a_test_with_default_arguments (thing =2 ,other =[3 ])$RET:
            pass

        class TestGroup :
            def test_has_self_and_default_args (self ,blah =None ,you =(3 ,4 ,
            5 ,5 ))$RET:
                # Test space is respected

                1 |should |be (2 )
        """

        assert_example(original, desired)

    def test_can_properly_dedent_after_block_of_just_containers(self):
        original = """
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
        def test_should_ensure_askers_are_None_or_boolean_or_string ()$RET:
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

        assert_example(original, desired)

    def test_it_doesnt_add_semicolon_after_noy_setup_if_not_necessary(self):
        original = """
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
        class TestBlockWithNecessarySemicolon :
            def setUp (self ):
                __import__ ("noseOfYeti").tokeniser .TestSetup (super ()).sync_before_each ();two =1 +1

        class TestBlockWithUnecessarySemiclon :
            def setUp (self ):
                __import__ ("noseOfYeti").tokeniser .TestSetup (super ()).sync_before_each ()#comment
                pass

            def tearDown (self ):
                __import__ ("noseOfYeti").tokeniser .TestSetup (super ()).sync_after_each ()
                pass
        """

        assert_example(original, desired)

    def test_it_keeps_comments_placed_after_setup_and_teardown_methods(self):
        original = """
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
        class TestKls :
            def setUp (self ):# Comment one
                __import__ ("noseOfYeti").tokeniser .TestSetup (super ()).sync_before_each ()
                pass

            def tearDown (self ):# Comment two
                __import__ ("noseOfYeti").tokeniser .TestSetup (super ()).sync_after_each ()
                pass

        class TestKls2 :
            def setUp (self ):# Comment three
                __import__ ("noseOfYeti").tokeniser .TestSetup (super ()).sync_before_each ();two =1 +1

            def tearDown (self ):# Comment four
                __import__ ("noseOfYeti").tokeniser .TestSetup (super ()).sync_after_each ()#comment
                pass
        """

        assert_example(original, desired)

    def test_it_doesnt_mess_up_dedent_from_whitespace_in_fstring(self):
        original = """
        def one(
            item: object, want: three, /, _register: four
        ) -> dict | None:
            f"{item} "


        def two(value: object, /) -> dict | None:
            return None
        """

        desired = """
        def one (
        item :object ,want :three ,/,_register :four
        )->dict |None :
            f"{item } "


        def two (value :object ,/)->dict |None :
            return None
        """

        if sys.version_info < (3, 12):
            desired = desired.replace("{item }", "{item}")

        assert_example(original, desired)
