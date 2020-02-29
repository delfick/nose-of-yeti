# coding: spec
# This is a comparison of dsl syntax to what is generated

########################
###   BEFORE
########################
# coding: spec

from unittest import TestCase

it 'can exist without a describe': pass

it 'can have args', blah=1: pass

describe TestCase, 'numbers':
    before_each:
        self.number1 = 1
        self.number2 = 2

    it 'has number1 as 1':
        self.assertEqual(self.number1, 1)

    ignore 'some test that I want to be named so it isnt ran':
        pass

    describe 'testing number 3':
        before_each:
            self.number3 = 3

        it 'has number1 from the lower level describe':
            self.assertEqual(self.number1, 1)

        it 'also has number3':
            self.assertEqual(self.number3, 3)

        it "works when I have non alphanumeric characters in the test name, things like ' or %":
            self.assertEqual(5, 5)

        it "can have arguments", arg1=2, arg2=4:
            self.assertEqual(arg2, 4)

        it "maintains newlines to keep line numbers same in exceptions":


            pass

        describe "let's change a number":
            before_each:

                self.number1 = 4

            it 'changed number1 but kept others the same':
                self.assertEqual(self.number1, 4)
                self.assertEqual(self.number2, 2)
                self.assertEqual(self.number3, 3)

########################
###   AFTER
### Note that I did clean it up very slightly
########################

from unittest import TestCase

def test_can_exist_without_a_describe(): pass

def test_can_have_args(blah=1): pass

class TestNumbers(TestCase):
    def setUp(self):
        __import__ ("noseOfYeti").TestSetup(super()).sync_before_each (); self.number1 = 1
        self.number2 = 2

    def test_has_number1_as_1(self):
        self.assertEqual(self.number1, 1)

    def ignore__some_test_that_I_want_to_be_named_so_it_isnt_ran(self):
        pass

class TestNumbers_TestingNumber3(TestNumbers):
    def setUp(self):
        __import__ ("noseOfYeti").TestSetup(super()).sync_before_each (); self.number3 = 3

    def test_has_number1_from_the_lower_level_describe(self):
        self.assertEqual(self.number1, 1)

    def test_also_has_number3 (self ):
        self.assertEqual(self.number3, 3)

    def test_works_when_I_have_non_alphanumeric_characters_in_the_test_name_things_like_or(self):
        self.assertEqual(5, 5)

    def test_can_have_arguments(self, arg1 = 2, arg2 = 4):
        self.assertEqual(arg2, 4)

    def test_maintains_newlines_to_keep_line_numbers_same_in_exceptions(self):


        pass

class TestNumbers_TestingNumber3_LetsChangeANumber(TestNumbers_TestingNumber3):
    def setUp(self):
        __import__ ("noseOfYeti").TestSetup(super()).sync_before_each ()
        self.number1 = 4

    def test_changed_number1_but_kept_others_the_same(self):
        self.assertEqual(self.number1, 4)
        self.assertEqual(self.number2, 2)
        self.assertEqual(self.number3, 3)

TestNumbers.is_noy_spec= True
TestNumbers_TestingNumber3.is_noy_spec= True
TestNumbers_TestingNumber3_LetsChangeANumber.is_noy_spec = True
TestNumbers_TestingNumber3.test_works_when_I_have_non_alphanumeric_characters_in_the_test_name_things_like_or.__func__.__testname__ = "works when I have non alphanumeric characters in the test name, things like ' or %"

