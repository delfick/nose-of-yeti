# coding: spec
# This is a comparison of dsl syntax to what is generated

########################
###   BEFORE
########################
# coding: spec

it 'can exist without a describe'

it 'can have args', blah

describe 'numbers':
    before_each:
        self.number1 = 1
        self.number2 = 2

    it 'should have number1 as 1':
        self.number1 |should| equal_to(1)

    ignore 'some test that I want to be named so it isnt ran':
        pass

    it 'should be skipped'

    describe 'testing number 3':
        before_each:
            self.number3 = 3

        it 'should have number1 from the lower level describe':
            self.number1 |should| equal_to(1)

        it 'should also have number3':
            self.number3 |should| equal_to(3)

        it "shouldn't fail when non alphanumeric characters are in the name":
            5 |should| be(5)

        it "can have arguments", arg1, arg2=4

        it "maintains newlines to keep line numbers same in exceptions"


            pass

        describe "let's change a number":
            before_each:

                self.number1 = 4

            it 'should have changed number1 but kept others':
                self.number1 |should| equal_to(4)
                self.number2 |should| equal_to(2)
                self.number3 |should| equal_to(3)

########################
###   AFTER
### Note that I did clean it up very slightly
########################

import nose; from nose.tools import *; from should_dsl import *; from noseOfYeti.noy_helper import *

def test_can_exist_without_a_describe(): raise nose.SkipTest

def test_can_have_args(blah): raise nose.SkipTest

class Test_numbers(object):
    def setUp(self):
        noy_sup_setUp (super (TestThing ,self )); self.number1 = 1
        self.number2 = 2

    def test_should_have_number1_as_1(self):
        self.number1 |should| equal_to(1)

    def ignore__some_test_that_I_want_to_be_named_so_it_isnt_ran(self):
        pass

    def test_should_be_skipped(self): raise nose.SkipTest

class Test_numbers_testing_number_3(Test_numbers):
    def setUp(self):
        noy_sup_setUp (super (TestThing ,self ))
        self.number3 = 3

    def test_should_have_number1_from_the_lower_level_describe(self):
        self.number1 | should| equal_to(1)

    def test_should_also_have_number3(self):
        self.number3 |should| equal_to(3)

    def test_shouldnt_fail_when_non_alphanumeric_characters_are_in_the_name(self):
        5 |should| be(5)

    def test_can_have_arguments(self, arg1, arg2=4): raise nose.SkipTest

    def test_maintains_newlines_to_keep_line_numbers_same_in_exceptions(self):


        pass

class Test_numbers_testing_number_3_lets_change_a_number(Test_numbers_testing_number_3):
    def setUp(self):
        noy_sup_setUp (super (TestThing ,self )); self.number1 =4

    def test_should_have_changed_number1_but_kept_others(self):
        self.number1 |should| equal_to(4)
        self.number2 |should| equal_to(2)
        self.number3 |should| equal_to(3)

Test_numbers.is_noy_spec = True
Test_numbers_testing_number_3.is_noy_spec = True
Test_numbers_testing_number_3_lets_change_a_number.is_noy_spec = True
Test_numbers_testing_number_3.test_shouldnt_fail_when_non_alphanumeric_characters_are_in_the_name.__func__.__testname__ = "shouldn't fail when non alphanumeric characters are in the name"

