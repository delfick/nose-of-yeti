# coding: spec

# You ensure the file has the coding: spec comment as the first line as above
# and that nose-of-yeti has registered the spec codec

# The codec will then turn what you have written into python code that can be
# executed.

# The test can then be specified using describes and its

from unittest import TestCase


def test_is_possible_to_add_numbers ():
    assert 1 +1 ==2

def test_is_possible_to_add_the_number_three (three =3 ):
    # Contrived example of default arguments
    assert 1 +three ==4

class TestPythonMathematics :
    # ^^ is replaced with "class test_Python_Mathematics:"

    def test_is_be_able_to_add_two_numbers (self ):
        # ^^ is replaced with "def test_is_able_to_add_two_numbers(self):"
        assert 2 +3 ==5
        assert 2 +0 ==2

    def test_cant_divide_by_zero (self ):
        try :
            2 /0
            assert False ,"Expected an error"
        except ZeroDivisionError :
            pass

# We can also define a class for the describes
# Either when we create the tokeniser and register it
# Or inside the spec file itself, per describe

class DifferentBase (TestCase ):
    def x (self ):
        return 5

class TestInheritance (DifferentBase ):
    def test_has_an_x_equal_to_5 (self ):
        self .assertEqual (self .x (),5 )

# You can even nest describes

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

TestPythonMathematics .is_noy_spec =True  # type: ignore
TestInheritance .is_noy_spec =True  # type: ignore
TestNumbers .is_noy_spec =True  # type: ignore
TestNumbers_TestingNumber3 .is_noy_spec =True  # type: ignore
TestNumbers_TestingNumber3_LetsChangeANumber .is_noy_spec =True  # type: ignore

TestPythonMathematics .test_cant_divide_by_zero .__testname__ ="can't divide by zero"  # type: ignore
