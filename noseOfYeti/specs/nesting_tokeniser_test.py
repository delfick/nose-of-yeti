from noseOfYeti.tokeniser import Tokeniser
from should_dsl import *
from matchers import *
 
class Test_Tokeniser_Nesting(object):
    def setUp(self):
        self.toka = Tokeniser(withDescribeAttrs=False)
        self.tokb = Tokeniser(withDescribeAttrs=False, defaultKls = 'other')
        
        ###   SMALL EXAMPLE (WITHOUT PASS)
        
        self.smallExample = [
        '''
        describe "This":
            describe "That":

                describe "Meh":pass
            context "Blah":pass
        describe "Another":pass '''
        ,
        '''
        class TestThis (%(o)s ):pass 
        class TestThis_That (TestThis ):pass 
        class TestThis_That_Meh (TestThis_That ):pass 
        class TestThis_Blah (TestThis ):pass 
        class TestAnother (%(o)s ):pass 
        '''
        ]
        
        ###   SMALL EXAMPLE (WITH PATH FOR BW COMPAT)
        
        self.smallExampleWithPass = [
        '''
        context "This":pass
            describe "That":pass
                describe "Meh":pass
            describe "Blah":pass
        describe "Another":pass '''
        ,
        '''
        class TestThis (%(o)s ):pass 
        class TestThis_That (TestThis ):pass 
        class TestThis_That_Meh (TestThis_That ):pass 
        class TestThis_Blah (TestThis ):pass 
        class TestAnother (%(o)s ):pass 
        '''
        ]
        
        ###   BIG EXAMPLE
        
        self.bigExample = [
        '''
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
        '''
        ,
        '''
        class TestThis (%(o)s ):
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
        class TestAnother (%(o)s ):
            def test_should (self ):
                if z :
                    if u :
                        print "hello \
                            there"
                    else :
                        print "no"
                else :
                    pass 
        '''
        ]
        
    ###   TESTS
    
    def test_it_should_work_with_space(self):
        test, desired = self.smallExample
        (self.toka, test) |should| result_in(desired % {'o' : 'object'})
        (self.tokb, test) |should| result_in(desired % {'o' : 'other'})
    
    def test_it_should_work_with_tabs(self):
        test, desired = [d.replace('    ', '\t') for d in self.smallExample]
        (self.toka, test) |should| result_in(desired % {'o' : 'object'})
        (self.tokb, test) |should| result_in(desired % {'o' : 'other'})
        
    def test_it_should_work_with_space_and_inline_pass(self):
        test, desired = self.smallExampleWithPass
        (self.toka, test) |should| result_in(desired % {'o' : 'object'})
        (self.tokb, test) |should| result_in(desired % {'o' : 'other'})
    
    def test_it_should_work_with_tabs_and_inline_pass(self):
        test, desired = [d.replace('    ', '\t') for d in self.smallExampleWithPass]
        (self.toka, test) |should| result_in(desired % {'o' : 'object'})
        (self.tokb, test) |should| result_in(desired % {'o' : 'other'})
        
    def test_it_should_keep_good_indentation_in_body_with_spaces(self):
        test, desired = self.bigExample
        (self.toka, test) |should| result_in(desired % {'o' : 'object'})
        (self.tokb, test) |should| result_in(desired % {'o' : 'other'})
        
    def test_it_should_keep_good_indentation_in_body_with_tabs(self):
        test, desired = [d.replace('    ', '\t') for d in self.bigExample]
        (self.toka, test) |should| result_in(desired % {'o' : 'object'})
        (self.tokb, test) |should| result_in(desired % {'o' : 'other'})
    
    def test_it_should_name_nested_describes_with_part_of_parents_name(self):
        test = 'describe "a":\n\tdescribe "b":'
        desired = 'class TestA (object ):pass \nclass TestA_B (TestA ):'
        (self.toka, test) |should| result_in(desired)