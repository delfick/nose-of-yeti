# coding: spec
# This is a comparison of dsl syntax to what is generated

########################
###   BEFORE
########################
# coding: spec

describe 'numbers':
    before_each:
        self.number1 = 1
        self.number2 = 2
    
    it 'should have number1 as 1':
        self.number1 | should.be | 1
    
    ignore 'some test that I want to be named so it isnt ran':
        pass
    
    it 'should be skipped'
    
    describe 'testing number 3':
        before_each:
            self.number3 = 3
        
        it 'should have number1 from the lower level describe':
            self.number1 | should.be | 1
        
        it 'should also have number3':
            self.number3 | should.be | 3
        
        describe "let's change a number":
            before_each:
                self.number1 = 4
            
            it 'should have changed number1 but kept others':
                self.number1 | should.be | 4
                self.number2 | should.be | 2
                self.number3 | should.be | 3

########################
###   AFTER
### Note that I did clean it up very slightly
########################

import nose; from nose.tools import *; from should_dsl import *

class Test_numbers(object):
    def setUp(self):
        sup = super(Test_numbers, self)
        if hasattr(sup, "setUp"): sup.setUp()
        self.number1 = 1
        self.number2 = 2

    def test_should_have_number1_as_1(self):
        self.number1 | should.be | 1

    def ignore__some_test_that_I_want_to_be_named_so_it_isnt_ran(self):
        pass

    def test_should_be_skipped(self): raise nose.SkipTest

class Test_testing_number_3(Test_numbers):
    def setUp(self):
        sup = super(Test_testing_number_3, self)
        if hasattr(sup, "setUp"): sup.setUp()
        self.number3 = 3

    def test_should_have_number1_from_the_lower_level_describe(self):
        self.number1 | should .be | 1

    def test_should_also_have_number3(self):
        self.number3 | should.be | 3

class Test_lets_change_a_number(Test_testing_number_3):
    def setUp(self):
        sup = super(Test_lets_change_a_number, self)
        if hasattr(sup, "setUp"): sup.setUp()
        self.number1 =4

    def test_should_have_changed_number1_but_kept_others(self):
        self.number1 | should.be | 4
        self.number2 | should.be | 2
        self.number3 | should.be | 3

Test_numbers.is_noy_spec = True
Test_testing_number_3.is_noy_spec = True
Test_lets_change_a_number.is_noy_spec = True
