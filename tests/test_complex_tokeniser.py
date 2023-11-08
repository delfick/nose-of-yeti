import pytest

from noseOfYeti.tokeniser.tokeniser import WITH_IT_RETURN_TYPE_ENV_NAME, Tokeniser


class Examples:
    small_example = [
        """
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
        describe "async":
            async before_each:
                pass
            async after_each:
                pass
    describe "Another":
        before_each:
            self.z = 8 """,
        """
    class TestThis :
        def setUp (self ):
            __import__ ("noseOfYeti").tokeniser .TestSetup (super ()).sync_before_each ();self .x =5
    class TestThis_That (TestThis ):
        def setUp (self ):
            __import__ ("noseOfYeti").tokeniser .TestSetup (super ()).sync_before_each ();self .y =6
    class TestThis_That_Meh (TestThis_That ):
        def tearDown (self ):
            __import__ ("noseOfYeti").tokeniser .TestSetup (super ()).sync_after_each ();self .y =None
    class TestThis_Blah (TestThis ):pass
    class TestThis_Async (TestThis ):
        async def setUp (self ):
            await __import__ ("noseOfYeti").tokeniser .TestSetup (super ()).async_before_each ();pass
        async def tearDown (self ):
            await __import__ ("noseOfYeti").tokeniser .TestSetup (super ()).async_after_each ();pass
    class TestAnother :
        def setUp (self ):
            __import__ ("noseOfYeti").tokeniser .TestSetup (super ()).sync_before_each ();self .z =8

    TestThis .is_noy_spec =True  # type: ignore
    TestThis_That .is_noy_spec =True  # type: ignore
    TestThis_That_Meh .is_noy_spec =True  # type: ignore
    TestThis_Blah .is_noy_spec =True  # type: ignore
    TestThis_Async .is_noy_spec =True  # type: ignore
    TestAnother .is_noy_spec =True  # type: ignore
    """,
    ]

    big_example = [
        """
    describe "This":
        before_each:
            self.x = 5
        it 'should':
            if x:
                pass
            else:
                x += 9
        async it 'supports async its':
            pass
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
    ignore "root level $pecial-method*+":
        pass
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
    async it 'supports level 0 async its':
        pass
    """,
        """
    class TestThis :
        def setUp (self ):
            __import__ ("noseOfYeti").tokeniser .TestSetup (super ()).sync_before_each ();self .x =5
        def test_should (self )$RET:
            if x :
                pass
            else :
                x +=9
        async def test_supports_async_its (self )$RET:
            pass
    class TestThis_That (TestThis ):
        def setUp (self ):
            __import__ ("noseOfYeti").tokeniser .TestSetup (super ()).sync_before_each ();self .y =6
    class TestThis_That_Meh (TestThis_That ):
        def tearDown (self ):
            __import__ ("noseOfYeti").tokeniser .TestSetup (super ()).sync_after_each ();self .y =None
        def test_should_set_testname_for_non_alpha_names (self )$RET:
            pass
        def test_should (self )$RET:
            if y :
                pass
            else :
                pass
        def test_should_have_args (self ,arg1 ,arg2 )$RET:
            blah |should |be_good ()
    class TestThis_Blah (TestThis ):pass
    def ignore__root_level_pecial_method ()$RET:
        pass
    class TestAnother :
        def setUp (self ):
            __import__ ("noseOfYeti").tokeniser .TestSetup (super ()).sync_before_each ();self .z =8
        def test_should (self )$RET:
            if z :
                if u :
                    print "hello \
                        there"
                else :
                    print "no"
            else :
                pass
    async def test_supports_level_0_async_its ()$RET:
        pass

    TestThis .is_noy_spec =True  # type: ignore
    TestThis_That .is_noy_spec =True  # type: ignore
    TestThis_That_Meh .is_noy_spec =True  # type: ignore
    TestThis_Blah .is_noy_spec =True  # type: ignore
    TestAnother .is_noy_spec =True  # type: ignore

    ignore__root_level_pecial_method .__testname__ ="root level $pecial-method*+"  # type: ignore
    TestThis_That_Meh .test_should_set_testname_for_non_alpha_names .__testname__ ="should set __testname__ for non alpha names ' $^"  # type: ignore
    """,
    ]

    comment_example = [
        """
    assertTileHues(
        self, tiles[0],
        25.0,  25.0,  25.0,  25.0,  25.0,  25.0, # noqa
        18.75, 18.75, 18.75, 18.75, 18.75, 18.75, # noqa
    )

    it "things":
        assertTileHues(
            self, tiles[1],
            25.0,  25.0,  25.0,  25.0,  25.0,  25.0, # noqa
            18.75, 18.75, 18.75, 18.75, 18.75, 18.75, # noqa
        )

        expected = {
            # something
            ("D2", "<d"): lambda s: ("D2", "<d", s)
            # something else
            ,
            ("B2", None): ("B2", None, None),
        }

        def t(n, f, c):
            return expected[(n, f, c)]

        assert True # type: ignore[valid-type]
        assert True

        # one two three
        assert True
    """,
        """
    assertTileHues (
    self ,tiles [0 ],
    25.0 ,25.0 ,25.0 ,25.0 ,25.0 ,25.0 ,# noqa
    18.75 ,18.75 ,18.75 ,18.75 ,18.75 ,18.75 ,# noqa
    )

    def test_things ()$RET:
        assertTileHues (
        self ,tiles [1 ],
        25.0 ,25.0 ,25.0 ,25.0 ,25.0 ,25.0 ,# noqa
        18.75 ,18.75 ,18.75 ,18.75 ,18.75 ,18.75 ,# noqa
        )

        expected ={
        # something
        ("D2","<d"):lambda s :("D2","<d",s )
        # something else
        ,
        ("B2",None ):("B2",None ,None ),
        }

        def t (n ,f ,c ):
            return expected [(n ,f ,c )]

        assert True # type: ignore[valid-type]
        assert True

        # one two three
        assert True
    """,
    ]


class Test_Tokeniser:
    def test_sets_with_it_return_type_appropriately(self, monkeypatch):
        monkeypatch.delenv(WITH_IT_RETURN_TYPE_ENV_NAME, raising=False)
        assert not Tokeniser().with_it_return_type

        monkeypatch.setenv(WITH_IT_RETURN_TYPE_ENV_NAME, "true")
        assert Tokeniser().with_it_return_type

        monkeypatch.setenv(WITH_IT_RETURN_TYPE_ENV_NAME, "false")
        assert not Tokeniser().with_it_return_type
        assert not Tokeniser().with_it_return_type

        monkeypatch.setenv(WITH_IT_RETURN_TYPE_ENV_NAME, "1")
        assert Tokeniser().with_it_return_type
        assert Tokeniser().with_it_return_type

        monkeypatch.setenv(WITH_IT_RETURN_TYPE_ENV_NAME, "0")
        assert not Tokeniser().with_it_return_type
        assert not Tokeniser().with_it_return_type

    def test_gives_describes_noy_specific_attributes(self):
        pytest.helpers.assert_example(
            [
                'describe "Something testable"',
                """
            class TestSomethingTestable :pass

            TestSomethingTestable .is_noy_spec =True  # type: ignore
            """,
            ]
        )


class Test_Tokeniser_Complex:
    def test_works_with_space(self):
        pytest.helpers.assert_example(Examples.small_example)

    def test_works_with_tabs(self):
        pytest.helpers.assert_example(Examples.small_example, convert_to_tabs=True)

    def test_keeps_good_indentation_in_body_with_spaces(self):
        pytest.helpers.assert_example(Examples.big_example)

    def test_keeps_good_indentation_in_body_with_tabs(self):
        pytest.helpers.assert_example(Examples.big_example, convert_to_tabs=True)

    def test_keeps_correct_indentation_with_comments(self):
        pytest.helpers.assert_example(Examples.comment_example, convert_to_tabs=True)
