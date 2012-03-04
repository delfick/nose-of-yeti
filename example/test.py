# coding: spec

# The "# coding: spec" is required to say that this file is encoded as a spec
# The tokeniser (I'm aussie, we spell it with an s :p) must be imported before this file
#  which is what the nose plugin does if the "--with-noy" option is specified

# When the file is parsed, the" # coding: spec"
#  is replaced with "import nose; from nose import *; from should_dsl import *"
# should-dsl is found here :: http://github.com/hugobr/should-dsl

# The test can then be specified using describes and its

it "is possible to add numbers":
    1 + 1 |should| be(2)

it "is possible to add the number three", three=3:
    # Contrived example of default arguments
    1 + three |should| be(4)

describe "Python Mathematics":
    # That is replaced with "class test_Python_Mathematics(object):"
    
    it 'should be able to add two numbers':
        # that is replaced with "def test_should_be_able_to_add_two_numbers(self):"
        (2 + 3) |should| equal_to(5)
        (2 + 0) |should| equal_to(2)
    
    it 'should not be able to divide by zero':
        lambda : 2 / 0 |should| throw(ZeroDivisionError)
    
    it 'should do this other thing'
    # Because it doesn't have colon at the end, it shouldn't be given a body and it will be replaced with
    #  "def test_should_do_this_other_thing(self): raise nose.SkipTest"

# We can also define a class for the describes
# Either when we create the tokeniser and register it
# Or inside the spec file itself, per describe

class DifferentBase(object):
    def x(self):
        return 5

describe DifferentBase 'Inheritance':
    it 'should have x equal to 5':
        self.x() |should| equal_to(5)

# You can even nest describes !
# The following is a bad example, but it demonstrates well enough

describe 'numbers':
    before_each:
        self.number1 = 1
        self.number2 = 2
    
    it 'should have number1 as 1':
        self.number1 |should| equal_to(1)
    
    describe 'testing number 3':
        before_each:
            self.number3 = 3
        
        it 'should have number1 from the lower level describe':
            self.number1 |should| equal_to(1)
        
        it 'should also have number3':
            self.number3 |should| equal_to(3)
        
        describe "let's change a number":
            before_each:
                self.number1 = 4
            
            it 'should have changed number1 but kept others':
                self.number1 |should| equal_to(4)
                self.number2 |should| equal_to(2)
                self.number3 |should| equal_to(3)

# Combined with the spec plugin from Pinnochio and it's corresponding --with-spec and --spec-color options
#  and should-dsl, we can achieve a very nice rspec style situation for python :D
# A nose 0.10.0 compatible version of that plugin can be found at :: 
#  http://groups.google.com/group/nose-users/browse_thread/thread/93e93cd1749a815b/b07206254a7bc767?lnk=gst&q=pinocchio#b07206254a7bc767
