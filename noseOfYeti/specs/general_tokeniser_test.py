from noseOfYeti.tokeniser import Tokeniser, determine_imports

from should_dsl import should, should_not
from tokenize import NEWLINE

# Silencing code checker about should_dsl matchers
contain = None
equal_to = None
result_in = None

class Test_Tokeniser(object):

    def test_gives_describes_noy_specific_attributes(self):
        imports = determine_imports(with_default_imports=False)
        tok = Tokeniser(import_tokens = imports)
        (tok, 'describe "Something testable"') |should| result_in(
        '''
        class TestSomethingTestable (object ):pass

        TestSomethingTestable .is_noy_spec =True
        '''
        )

    def test_is_possible_to_turn_off_attributes(self):
        imports = determine_imports(with_default_imports=False)
        tok = Tokeniser(import_tokens=imports, with_describe_attrs=False)
        (tok, 'describe "Something testable"') |should| result_in('class TestSomethingTestable (object ):pass')

    def test_no_newline_in_default_imports(self):
        tok = Tokeniser(import_tokens=determine_imports())
        tok.import_tokens |should_not| contain([NEWLINE, '\n'])

    def test_no_newline_in_extended_default_imports(self):
        imports = determine_imports(extra_imports='import another.class', with_default_imports=True)
        tok = Tokeniser(import_tokens=imports)
        tok.import_tokens |should_not| contain([NEWLINE, '\n'])
        (tok, '') |should| result_in(
            'import another .class ;import nose ;from nose .tools import *;from noseOfYeti .tokeniser .support import *'
        )

    def test_tokeniser_has_no_default_imports_by_default(self):
        tok = Tokeniser()
        tok.import_tokens |should| equal_to(None)

    def test_is_possible_to_specify_extra_imports_without_default_imports(self):
        imports = determine_imports(with_default_imports=False, extra_imports="import thing")
        tok = Tokeniser(import_tokens = imports)
        (tok, '') |should| result_in('import thing ')

    def test_determine_imports_imports_nothing_by_default(self):
        imports = determine_imports()
        tok = Tokeniser(import_tokens=imports)
        (tok, '') |should| result_in('')

