from noseOfYeti.tokeniser import Tokeniser
from should_dsl import should

# Silencing code checker about should_dsl matchers
equal_to = None
result_in = None


class Test_Tokeniser_Nesting(object):
    def setUp(self):
        self.toka = Tokeniser(with_describe_attrs=False)

        ###   SMALL EXAMPLE (WITHOUT PASS)

        self.small_example = [
            """
        describe "This":
            describe "That":

                describe "Meh":pass
            describe "Blah":pass
        describe "Another":pass """,
            """
        class TestThis ():pass
        class TestThis_That (TestThis ):pass
        class TestThis_That_Meh (TestThis_That ):pass
        class TestThis_Blah (TestThis ):pass
        class TestAnother ():pass
        """,
        ]

        ###   SMALL EXAMPLE (WITH PATH FOR BW COMPAT)

        self.small_example_with_pass = [
            """
        describe "This":pass
            describe "That":pass
                describe "Meh":pass
            describe "Blah":pass
        describe "Another":pass """,
            """
        class TestThis ():pass
        class TestThis_That (TestThis ):pass
        class TestThis_That_Meh (TestThis_That ):pass
        class TestThis_Blah (TestThis ):pass
        class TestAnother ():pass
        """,
        ]

        ###   BIG EXAMPLE

        self.big_example = [
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
        class TestThis ():
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
        class TestAnother ():
            def test_should (self ):
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

    ###   TESTS

    def test_works_with_space(self):
        test, desired = self.small_example
        (self.toka, test) | should | result_in(desired)

    def test_works_with_tabs(self):
        test, desired = [d.replace("    ", "\t") for d in self.small_example]
        (self.toka, test) | should | result_in(desired)

    def test_works_with_space_and_inline_pass(self):
        test, desired = self.small_example_with_pass
        (self.toka, test) | should | result_in(desired)

    def test_works_with_tabs_and_inline_pass(self):
        test, desired = [d.replace("    ", "\t") for d in self.small_example_with_pass]
        (self.toka, test) | should | result_in(desired)

    def test_keeps_good_indentation_in_body_with_spaces(self):
        test, desired = self.big_example
        (self.toka, test) | should | result_in(desired)

    def test_keeps_good_indentation_in_body_with_tabs(self):
        test, desired = [d.replace("    ", "\t") for d in self.big_example]
        (self.toka, test) | should | result_in(desired)

    def test_names_nested_describes_with_part_of_parents_name(self):
        test = 'describe "a":\n\tdescribe "b":'
        desired = "class TestA ():pass\nclass TestA_B (TestA ):"
        (self.toka, test) | should | result_in(desired)
