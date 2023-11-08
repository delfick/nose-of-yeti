# coding: spec

# You ensure the file has the coding: spec comment as the first line as above
# and that nose-of-yeti has registered the spec codec

# The codec will then turn what you have written into python code that can be
# executed.

# The test can then be specified using describes and its

from unittest import TestCase


it "is possible to add numbers":
    assert 1 + 1 == 2

it "is possible to add the number three", three=3:
    # Contrived example of default arguments
    assert 1 + three == 4

describe "Python Mathematics":
    # ^^ is replaced with "class test_Python_Mathematics:"

    it 'is be able to add two numbers':
        # ^^ is replaced with "def test_is_able_to_add_two_numbers(self):"
        assert 2 + 3 == 5
        assert 2 + 0 == 2

    it "can't divide by zero":
        try:
            2 / 0
            assert False, "Expected an error"
        except ZeroDivisionError:
            pass

# We can also define a class for the describes
# Either when we create the tokeniser and register it
# Or inside the spec file itself, per describe

class DifferentBase(TestCase):
    def x(self):
        return 5

describe DifferentBase 'Inheritance':
    it 'has an x equal to 5':
        self.assertEqual(self.x(), 5)

# You can even nest describes

describe TestCase, 'numbers':
    before_each:
        self.number1 = 1
        self.number2 = 2

    it 'has number1 as 1':
        self.assertEqual(self.number1, 1)

    describe 'testing number 3':
        before_each:
            self.number3 = 3

        it 'has number1 from the lower level describe':
            self.assertEqual(self.number1, 1)

        it 'also has number3':
            self.assertEqual(self.number3, 3)

        describe "let's change a number":
            before_each:
                self.number1 = 4

            it 'changed number1 but kept others':
                self.assertEqual(self.number1, 4)
                self.assertEqual(self.number2, 2)
                self.assertEqual(self.number3, 3)
