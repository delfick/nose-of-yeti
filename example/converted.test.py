# coding: spec

# The noy plugin for nosetests (enabled by the --with-noy option)
# will register the "spec" codec, which means any file that has
# "# coding: sepc" as the first line, like this file, will be parsed
# by the spec codec before it is imported.

# The codec will then turn what you have written into proper
# , executable python code!

# The test can then be specified using describes and its

from unittest import TestCase

def test_is_possible_to_add_numbers ():
    assert 1 +1 ==2

def test_is_possible_to_add_the_number_three (three =3 ):
    # Contrived example of default arguments
    assert 1 +three ==4

class TestPythonMathematics (TestCase ):
    # That is replaced with "class test_Python_Mathematics(object):"

    def test_is_be_able_to_add_two_numbers (self ):
        # that is replaced with "def test_is_able_to_add_two_numbers(self):"
        self .assertEqual (2 +3 ,5 )
        self .assertEqual (2 +0 ,2 )

    def test_cant_divide_by_zero (self ):
        with self .assertRaises (ZeroDivisionError ):
            2 /0

# We can also define a class for the describes
# Either when we create the tokeniser and register it
# Or inside the spec file itself, per describe

class DifferentBase (TestCase ):
    def x (self ):
        return 5

class TestInheritance (DifferentBase ):
    def test_has_an_x_equal_to_5 (self ):
        self .assertEqual (self .x (),5 )

# You can even nest describes !
# The following is a bad example, but it demonstrates well enough

class TestNumbers (TestCase ):
    def setUp (self ):
        __import__ ("noseOfYeti").tokeniser .TestSetup (super ()).sync_before_each ();self .number1 =1
        self .number2 =2

    def test_has_number1_as_1 (self ):
        self .assertEqual (self .number1 ,1 )

class TestNumbers_TestingNumber3 (TestNumbers ):
    def setUp (self ):
        __import__ ("noseOfYeti").tokeniser .TestSetup (super ()).sync_before_each ();self .number3 =3

    def test_has_number1_from_the_lower_level_describe (self ):
        self .assertEqual (self .number1 ,1 )

    def test_also_has_number3 (self ):
        self .assertEqual (self .number3 ,3 )

class TestNumbers_TestingNumber3_LetsChangeANumber (TestNumbers_TestingNumber3 ):
    def setUp (self ):
        __import__ ("noseOfYeti").tokeniser .TestSetup (super ()).sync_before_each ();self .number1 =4

    def test_changed_number1_but_kept_others (self ):
        self .assertEqual (self .number1 ,4 )
        self .assertEqual (self .number2 ,2 )
        self .assertEqual (self .number3 ,3 )

TestPythonMathematics .is_noy_spec =True
TestInheritance .is_noy_spec =True
TestNumbers .is_noy_spec =True
TestNumbers_TestingNumber3 .is_noy_spec =True
TestNumbers_TestingNumber3_LetsChangeANumber .is_noy_spec =True

TestPythonMathematics .test_cant_divide_by_zero .__testname__ ="can't divide by zero"
