import pytest


class Examples:
    small_example = [
        """
    describe "This":
        describe "That":

            describe "Meh":pass
        describe "Blah":pass
    describe "Another":pass """,
        """
    class TestThis :pass
    class TestThis_That (TestThis ):pass
    class TestThis_That_Meh (TestThis_That ):pass
    class TestThis_Blah (TestThis ):pass
    class TestAnother :pass
    """,
    ]

    ###   SMALL EXAMPLE (WITH PATH FOR BW COMPAT)

    small_example_with_pass = [
        """
    describe "This":pass
        describe "That":pass
            describe "Meh":pass
        describe "Blah":pass
    describe "Another":pass """,
        """
    class TestThis :pass
    class TestThis_That (TestThis ):pass
    class TestThis_That_Meh (TestThis_That ):pass
    class TestThis_Blah (TestThis ):pass
    class TestAnother :pass
    """,
    ]

    big_example = [
        """
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
    """,
        """
    class TestThis :
        def test_should (self )$RET:
            if x :
                pass
            else :
                x +=9
    class TestThis_That (TestThis ):pass
    class TestThis_That_Meh (TestThis_That ):
        def test_should (self )$RET:
            if y :
                pass
            else :
                pass
    class TestThis_Blah (TestThis ):pass
    class TestAnother :
        def test_should (self )$RET:
            if z :
                if u :
                    print "hello \
                        there"
                else :
                    print "no"
            else :
                pass
    """,
    ]


def assert_example(example, convert_to_tabs=False):
    __tracebackhide__ = True
    pytest.helpers.assert_example(
        example, convert_to_tabs=convert_to_tabs, with_describe_attrs=False
    )


class Test_Tokeniser_Nesting:
    def test_works_with_space(self):
        assert_example(Examples.small_example)

    def test_works_with_tabs(self):
        assert_example(Examples.small_example, convert_to_tabs=True)

    def test_works_with_space_and_inline_pass(self):
        assert_example(Examples.small_example_with_pass)

    def test_works_with_tabs_and_inline_pass(self):
        assert_example(Examples.small_example_with_pass, convert_to_tabs=True)

    def test_keeps_good_indentation_in_body_with_spaces(self):
        assert_example(Examples.big_example)

    def test_keeps_good_indentation_in_body_with_tabs(self):
        assert_example(Examples.big_example, convert_to_tabs=True)

    def test_names_nested_describes_with_part_of_parents_name(self):
        original = 'describe "a":\n\tdescribe "b":'
        desired = "class TestA :pass\nclass TestA_B (TestA ):"
        assert_example([original, desired])
