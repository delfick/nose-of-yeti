from noseOfYeti.plugins.support.test_chooser import TestChooser
from should_dsl import *

class Test_TestChooser(object):
    
    def setup(self):
        self.test_chooser = TestChooser()
    
    def test_it_resets_done_when_told_about_new_module(self):
        self.test_chooser.done |should| equal_to({})
        self.test_chooser.done['a'] = 3
        self.test_chooser.done |should| equal_to({'a':3})
        self.test_chooser.new_module()
        self.test_chooser.done |should| equal_to({})
        
    def test_already_visited_puts_kls_name_key_in_done_or_returns_True(self):
        self.test_chooser.done |should| equal_to({})
        self.test_chooser.already_visited('a', 'b') |should| be(False)
        self.test_chooser.done |should| equal_to({'a.b' : True})
        self.test_chooser.already_visited('a', 'b') |should| be(True)
        
        self.test_chooser.already_visited('c', 'd') |should| be(False)
        self.test_chooser.done |should| equal_to({'a.b' : True, 'c.d' : True})
        self.test_chooser.already_visited('c', 'd') |should| be(True)

class Test_TestChooser_Consider(object):
    __childof__ = Test_TestChooser
    __testname__ = ".consider() method"
    
    def setup(self):
        self.test_chooser = TestChooser()
        class TestKlsForTest(object):
            def ignore__test(self): pass
            
            def test_with__test__set(self): pass
            test_with__test__set.__test__ = False
            
            def test_actual(self): pass
        
        class TestIgnoredKls(object):
            def test_things(self): pass
        
        class TestKlsWithInherited(TestKlsForTest):
            def test_on_subclass(self): pass
        
        self.TestKlsForTest = TestKlsForTest
        self.TestIgnoredKls = TestIgnoredKls
        self.TestKlsWithInherited = TestKlsWithInherited
    
    def test_it_ignores_if_method_starts_with_ignore(self):
        self.test_chooser.consider(self.TestKlsForTest().ignore__test) |should| be(False)
    
    def test_it_ignores_if_method_has__test__set_to_false(self):
        self.test_chooser.consider(self.TestKlsForTest().test_with__test__set) |should| be(False)
    
    def test_it_ignores_if_method_has_kls_in_ignoreKls(self):
        self.TestIgnoredKls.is_noy_spec = True
        self.test_chooser.consider(self.TestIgnoredKls().test_things) |should| be(True)
        self.test_chooser.consider(self.TestIgnoredKls().test_things, ignore_kls=['TestIgnoredKls']) |should| be(False)
    
    def test_it_returns_None_if_kls_does_not_have_is_noy_test_set(self):
        self.test_chooser.consider(self.TestKlsForTest().test_actual) |should| be(None)
    
    def test_it_ignores_inherited_tests_if_is_noy_test_is_set_on_kls(self):
        self.test_chooser.consider(self.TestKlsWithInherited().test_actual) |should| be(None)
        self.TestKlsWithInherited.is_noy_spec = True
        self.test_chooser.consider(self.TestKlsWithInherited().test_actual) |should| be(False)
        self.test_chooser.consider(self.TestKlsWithInherited().test_on_subclass) |should| be(True)
    
    def test_it_ignores_functions_already_visited(self):
        self.TestKlsWithInherited.is_noy_spec = True
        self.test_chooser.consider(self.TestKlsWithInherited().test_on_subclass) |should| be(True)
        self.test_chooser.consider(self.TestKlsWithInherited().test_on_subclass) |should| be(False)