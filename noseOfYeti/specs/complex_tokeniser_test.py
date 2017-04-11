from noseOfYeti.tokeniser import Tokeniser
from should_dsl import should

import six

# Silencing code checker about should_dsl matchers
result_in = None

func_accessor = ""
if six.PY2:
    func_accessor = "__func__ ."

class Test_Tokeniser_Complex(object):
    def setUp(self):
        self.toka = Tokeniser()
        self.tokb = Tokeniser(default_kls = 'other')

        ###   SMALL EXAMPLE

        self.small_example = [
        '''
        describe "This":
            before_each:
                self.x = 5
            describe "That":
                before_each:
                    self.y = 6
                describe "Meh":
                    after_each:
                        self.y = None
            describe "Blah":pass
            describe "async":
                async before_each:
                    pass
                async after_each:
                    pass
        describe "Another":
            before_each:
                self.z = 8 '''
        ,
        '''
        class TestThis (%(o)s ):
            def setUp (self ):
                noy_sup_setUp (super (TestThis ,self ));self .x =5
        class TestThis_That (TestThis ):
            def setUp (self ):
                noy_sup_setUp (super (TestThis_That ,self ));self .y =6
        class TestThis_That_Meh (TestThis_That ):
            def tearDown (self ):
                noy_sup_tearDown (super (TestThis_That_Meh ,self ));self .y =None
        class TestThis_Blah (TestThis ):pass
        class TestThis_Async (TestThis ):
            async def setUp (self ):
                await async_noy_sup_setUp (super (TestThis_Async ,self ));pass
            async def tearDown (self ):
                await async_noy_sup_tearDown (super (TestThis_Async ,self ));pass
        class TestAnother (%(o)s ):
            def setUp (self ):
                noy_sup_setUp (super (TestAnother ,self ));self .z =8

        TestThis .is_noy_spec =True
        TestThis_That .is_noy_spec =True
        TestThis_That_Meh .is_noy_spec =True
        TestThis_Blah .is_noy_spec =True
        TestThis_Async .is_noy_spec =True
        TestAnother .is_noy_spec =True
        '''
        ]

        ###   BIG EXAMPLE

        self.big_example = [
        '''
        describe "This":
            before_each:
                self.x = 5
            it 'should':
                if x:
                    pass
                else:
                    x += 9
            async it 'supports async its':
                pass
            describe "That":
                before_each:
                    self.y = 6
                describe "Meh":
                    after_each:
                        self.y = None
                    it "should set __testname__ for non alpha names ' $^":
                        pass
                    it 'should':
                        if y:
                            pass
                        else:
                            pass
                    it 'should have args', arg1, arg2:
                        blah |should| be_good()
            describe "Blah":pass
        ignore "root level $pecial-method*+"
        describe "Another":
            before_each:
                self.z = 8
            it 'should':
                if z:
                    if u:
                        print "hello \
                            there"
                    else:
                        print "no"
                else:
                    pass
        async it 'supports level 0 async its':
            pass
        '''
        ,
        '''
        class TestThis (%(o)s ):
            def setUp (self ):
                noy_sup_setUp (super (TestThis ,self ));self .x =5
            def test_should (self ):
                if x :
                    pass
                else :
                    x +=9
            async def test_supports_async_its (self ):
                pass
        class TestThis_That (TestThis ):
            def setUp (self ):
                noy_sup_setUp (super (TestThis_That ,self ));self .y =6
        class TestThis_That_Meh (TestThis_That ):
            def tearDown (self ):
                noy_sup_tearDown (super (TestThis_That_Meh ,self ));self .y =None
            def test_should_set_testname_for_non_alpha_names (self ):
                pass
            def test_should (self ):
                if y :
                    pass
                else :
                    pass
            def test_should_have_args (self ,arg1 ,arg2 ):
                blah |should |be_good ()
        class TestThis_Blah (TestThis ):pass
        def ignore__root_level_pecial_method ():raise nose.SkipTest
        class TestAnother (%(o)s ):
            def setUp (self ):
                noy_sup_setUp (super (TestAnother ,self ));self .z =8
            def test_should (self ):
                if z :
                    if u :
                        print "hello \
                            there"
                    else :
                        print "no"
                else :
                    pass
        async def test_supports_level_0_async_its ():
            pass

        TestThis .is_noy_spec =True
        TestThis_That .is_noy_spec =True
        TestThis_That_Meh .is_noy_spec =True
        TestThis_Blah .is_noy_spec =True
        TestAnother .is_noy_spec =True
        ignore__root_level_pecial_method .__testname__ ="root level $pecial-method*+"
        TestThis_That_Meh .test_should_set_testname_for_non_alpha_names .{func_accessor}__testname__ ="should set __testname__ for non alpha names ' $^"
        '''.format(func_accessor=func_accessor)
        ]

    ###   TESTS

    def test_works_with_space(self):
        test, desired = self.small_example
        (self.toka, test) |should| result_in(desired % {'o' : 'object'})
        (self.tokb, test) |should| result_in(desired % {'o' : 'other'})

    def test_works_with_tabs(self):
        test, desired = [d.replace('    ', '\t') for d in self.small_example]
        (self.toka, test) |should| result_in(desired % {'o' : 'object'})
        (self.tokb, test) |should| result_in(desired % {'o' : 'other'})

    def test_keeps_good_indentation_in_body_with_spaces(self):
        test, desired = self.big_example
        (self.toka, test) |should| result_in(desired % {'o' : 'object'})
        (self.tokb, test) |should| result_in(desired % {'o' : 'other'})

    def test_keeps_good_indentation_in_body_with_tabs(self):
        test, desired = [d.replace('    ', '\t') for d in self.big_example]
        (self.toka, test) |should| result_in(desired % {'o' : 'object'})
        (self.tokb, test) |should| result_in(desired % {'o' : 'other'})

