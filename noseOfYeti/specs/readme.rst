Tests
=====

To run the tests, execute the ``test.sh`` script in the root directory.

The majority of my tests are black box tests that ensure given a particular fragment of code, a particular output is achieved. To do this, I created a custom should_dsl matcher that will let me do this::

    class Test_Tokenisor_translation(object):
        def setUp(self):
            self.toka = Tokeniser(with_describe_attrs=False)

        def test_it_should_translate_a_describe(self):
            (self.toka, 'describe "Something testable"') |should| result_in('class TestSomethingTestable (object ):pass')

The matcher takes (tokeniser, original) on the left and expects a string on the right. It will use the tokeniser provided to translate the original string, followed by comparing that result to the string on the right.

.. note:: NoseOfYeti doesn't have any say on space between tokens and so the output can have some weird spacing.
