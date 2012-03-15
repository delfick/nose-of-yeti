.. _features:

Features
========

describe and context
--------------------

To group a bunch of tests together you can use the describe or context keywords::

    describe "Some Test":
        it "does things":
            assert 1 == 1
    
    context "Some Context":
        it "does other things":
            assert 2 == 2

Will be converted into classes where each test under the group becomes a method prefixed with test\_::

    class Test_SomeTest(object):
        def test_does_things(self):
            assert 1 == 1
    
    class Test_SomeContext(object):
        def test_does_other_things(self):
            assert 2 == 2

The class that is inherited can be changed by putting the name of the super class between the describe keyword and the name of the group::

    describe NiceTestCase "name": pass

becomes::

    class TestName(NiceTestCase): pass

The default class to inherit from is ``object``, however this can be changed with the :ref:`default-kls option <options>`.

Describe and context blocks can also be nested. The way this works is that each nested level will inherit from the class of the previous level. Then, to ensure that tests from inherited super classes aren't run multiple times, a special ``is_noy_spec`` attribute is set on each class and the nose plugin will ensure only methods defined on the class itself will be run::

    describe "NestedOne":
        it "has test"
        
        describe "NestedTwo":
            it "also has test"
            
            context "You get the point":
                it "ladelalalal"

becomes::
    
    class Test_NestedOne(object):
        def test_has_test(self): raise nose.skipTest
    
    class Test_NestedOne_NestedTwo(NestedOne):
        def test_also_has_test(self): raise nose.skipTest
    
    class Test_NestedOne_NestedTwo_You_get_the_point(Test_NestedOne_NestedTwo):
        def test_ladelalalal(self): raise nose.skipTest
        
    Test_NestedOne.is_noy_spec = True
    Test_NestedOne_NestedTwo.is_noy_spec = True
    Test_NestedOne_NestedTwo_You_get_the_point.is_noy_spec = True

It will prevent nested classes from having the same name as non-nested classes by prefixing the name of the class with the name of the class it inherits from.

it and ignore
-------------

The tests themselves can be specified with ``it`` or ``ignore`` in a similar fashion to ``describe`` and ``context``::

    it "is a test without a describe":
        # Note that it doesn't have a self paramater
        pass
    
    # This function has no colon, it raises nose.SkipTest
    it "is a method without a colon"
    
    describe "AGroup":
        it "is a test with a describe":
            # Note that it does have a self parameter
            pass
        
        ignore "ignored method":
            # This method is named ignore__%s
            assert 1 == 3
        
        # This method has no colon, it raises nose.SkipTest
        it "is a test without a colon"

becomes::
    
    def test_is_a_test_without_a_describe":
        # Note that it doesn't have a self parameter
        pass
    
    # This function has no colon, it raises nose.SkipTest
    def test_is_a_method_without_a_colon(): raise nose.SkipTest
    
    class Test_AGroup(object):
        def test_is_a_test_with_a_describe(self):
            # Note that it does have a self parameter
            pass
        
        def ignore__ignored_method(self):
            # This method is named ignore__%s
            assert 1 == 3
        
        # This method has no colon, it raises nose.SkipTest
        def test_is_a_test_without_a_colon(self): raise nose.SkipTest
    
    Test_AGroup.is_noy_spec = True

As shown in the example:
 * ``it "name"`` converts to ``def test_name``
 * ``ignore "name""`` converts to ``def ignore__name``
 * If it is part of a describe block, it is given a ``self`` parameter
 * If it has no colon, it raises nose.SkipTest

NoseOfYeti can also cope with non-alphanumeric characters in the name of a test, by removing them from the function name, and then setting ``__testname__`` on the function/method later on::
    
    it "won't don't $houldn't"
    
    describe "Blah":
        it "copes with 1!2@3#"
        
becomes::
    
    def test_wont_dont_houldnt(): raise nose.SkipTest
    
    class Test_Blah(object):
        def test_copes_with_123(self): raise nose.SkipTest
    
    test_wont_dont_houldnt.__testname__ = "won't don't $houldn't"
    Test_Blah.test_copes_with_123.__testname__ = "copes with 1!2@3#"

The ``__testname__`` attribute can then be used by nose to print out the names of tests when it runs them.

Extra parameters
----------------

NoseOfYeti is also able to cope with making tests accept other parameters. This is useful if you use decorators that do this::

    @fudge.patch("MyAwesomeModule.AwesomeClass")
    it "takes in a patched object", fakeAwesomeClass:
        fakeAwesomeClass.expects_call().returns_fake().expects('blah').with_args(1)
        fakeAwesomeClass().blah(1)
    
    describe "Blah":
        @fudge.patch("sys")
        it "also works with self", fakeSys:
            path = fudge.Fake('path')
            fakeSys.expects("path").returns(path)
            myFunction() |should| be(path)
        
        it "handles default arguments", thing=3, other=4:
            thing |should_not| be(other)

becomes::
    
    @fudge.patch("MyAwesomeModule.AwesomeClass")
    def test_takes_in_a_patched_object(fakeAwesomeClass):
        fakeAwesomeClass.expects_call().returns_fake().expects('blah').with_args(1)
        fakeAwesomeClass().blah(1)
    
    class Test_Blah(object):
        @fudge.patch("sys")
        def test_also_works_with_self(self, fakeSys):
            path = fudge.Fake('path')
            fakeSys.expects("path").returns(path)
            myFunction() |should| be(path)
        
        def test_handles_default_arguments(self, thing=3, other=4):
            thing |should_not| be(other)

Note that it will also cope with multiline lists as default parameters::

    it "has a contrived default argument", thing = [
        1
        , 2
        , 3
        ]

becomes::

    def test_has_a_contrived_default_argument(thing=[
        1
        , 2
        , 3
        ]): raise nose.SkipTest

.. _before_and_after_each:       

before_each and after_each
--------------------------

NoseOfYeti will turn ``before_each`` and ``after_each`` into ``setUp`` and ``tearDown`` respectively.

It will also make sure the ``setUp``/``tearDown`` method of the super class (if it has one) gets called as the first thing in a ``before_each``/``after_each``::
    
    describe "Meh":
        before_each:
            doSomeSetup()
        
        after_each:
            doSomeTearDown()

becomes::
    
    class Test_Meh(object):
        def setUp(self):
            noy_sup_setUp(super(Test_Meh, self)); doSomeSetup()
        
        def tearDown(self):
            noy_sup_tearDown(super(Test_Meh, self)); doSomeTearDown()

An example of a class that does have it's own ``setUp`` and ``tearDown`` functions is ``unittest.TestCase``. Use :ref:`default-kls option <options>` to set this as a default.

.. note:: 
    To ensure that line numbers between the spec and translated output are the same, the first line of a ``setUp``/``tearDown`` will be placed on the same line as the inserted super call. This means if you don't want pylint to complain about multiple statements on the same line or you want to define a function inside ``setUp``/``tearDown``, then just don't do it on the first line after ``before_each``/``after_each``::

        describe "Thing":
            before_each:
                # Comments are put on the same line, but no semicolon is inserted
            
            after_each:
            
                # Blank line after the after_each
                self.thing = 4

    becomes::
        
        class Test_Meh(unittest.TestCase):
            def setUp(self):
                noy_sup_setUp(super(Test_Meh, self)) # Comments are put on the same line, but no semicolon is inserted
            
            def tearDown(self):
                noy_sup_tearDown(super(Test_Meh, self))
                # Blank line after the after_each
                self.thing = 4

Also, remember if you use the :ref:`no-default-imports option <options>` then you'll have to manually import ``noy_sup_setUp`` and ``noy_sup_tearDown`` by doing ``from noseOfYeti.tokeniser.support import noy_sup_setUp, noy_sup_tearDown``

.. note::
    Anything on the same line as a ``before_each``/``after_each`` will remain on that line

        describe "Thing":
            before_each: # pylint: disable-msg: C0103

    becomes::
        
        class Test_Meh(unittest.TestCase):
            def setUp(self): # pylint: disable-msg: C0103
                noy_sup_setUp(super(Test_Meh, self))
    
Default imports
---------------

Unless you have :ref:`no-default-imports option <options>` set to True then by default, the following will be imported at the top of the spec file::
    
    import nose; from nose.tools import *; from noseOfYeti.tokeniser.support import *

If you also don't have :ref:`without-should-dsl option <options>` set, then it will do ``from should_dsl import *`` for you.

Line numbers
------------

With many thanks to work by ``jerico_dev`` (https://bitbucket.org/delfick/nose-of-yeti/changeset/ebf4e335bb1c), noseOfYeti will ensure that the line numbers line up between spec files and translated output. It does this by doing the following:

 * Default imports are all placed on the same line where ``# coding: spec`` is in the original file. If you have pylint complaining about multiple statements on a single line, it is suggested you use the :ref:`no-default-imports option <options>` and import things manually.
 
 * As mentioned :ref:`above <before_and_after_each>`, lines after a ``before_each`` or ``after_each`` will be placed on the same line as the inserted super call.
 
 * Setting ``is_noy_spec`` on classes and ``__testname__`` on tests happen at the end of the file after all the other code.