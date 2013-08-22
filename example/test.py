# coding: spec

# The noy plugin for nosetests (enabled by the --with-noy option)
# will register the "spec" codec, which means any file that has
# "# coding: sepc" as the first line, like this file, will be parsed
# by the spec codec before it is imported.

# The codec will then turn what you have written into proper
# , executable python code!

# The test can then be specified using describes and its

import nose

it "is possible to add numbers":
    self.assertEqual(1 + 1, 2)

it "is possible to add the number three", three=3:
    # Contrived example of default arguments
    self.assertEqual(1 + three, 4)

describe "Python Mathematics":
    # That is replaced with "class test_Python_Mathematics(object):"

    it 'is be able to add two numbers':
        # that is replaced with "def test_is_able_to_add_two_numbers(self):"
        self.assertEqual(2 + 3, 5)
        self.assertEqual(2 + 0, 2)

    it "can't divide by zero":
        with self.assertRaises(ZeroDivisionError):
            2 / 0

    it 'does this other thing'
    # Because it doesn't have colon at the end it will be a skipped test.
    # Which means it adds a raise nose.SkipTest for you
    #  "def test_does_this_other_thing(self): raise nose.SkipTest"
    # Note that if you don't have the "with-default-imports" option set,
    # then it is up to you to import nose

# We can also define a class for the describes
# Either when we create the tokeniser and register it
# Or inside the spec file itself, per describe

class DifferentBase(object):
    def x(self):
        return 5

describe DifferentBase 'Inheritance':
    it 'has an x equal to 5':
        self.assertEqual(self.x(), 5)

# You can even nest describes !
# The following is a bad example, but it demonstrates well enough

describe 'numbers':
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

