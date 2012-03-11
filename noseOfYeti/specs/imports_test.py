from noseOfYeti.tokeniser.imports import determine_imports
from tokenize import NEWLINE, NAME, OP
from should_dsl import *

class Test_DetermineImports(object):
    def test_extra_imports_are_added(self):
        extra_imports = "import thing; import stuff"
        determine_imports(
            extra_imports=extra_imports, with_default_imports=False, without_should_dsl=True
        ) |should| equal_to([
            (NAME, 'import'), (NAME, 'thing'), (OP, ';'), (NAME, 'import'), (NAME, 'stuff')
        ])
    
    def test_extra_imports_added_before_defaults(self):
        extra_imports = "import thing; import stuff"
        determine_imports(
            extra_imports=extra_imports, with_default_imports=True, without_should_dsl=True
        ) |should| equal_to([
              (NAME, 'import'), (NAME, 'thing'), (OP, ';'), (NAME, 'import'), (NAME, 'stuff')
            , (OP, ';') # Extra semicolon inserted
            , (NAME, 'import'), (NAME, 'nose'), (OP, ';')
            , (NAME, 'from'), (NAME, 'nose'), (OP, '.'), (NAME, 'tools'), (NAME, 'import'), (OP, '*'), (OP, ';')
            , (NAME, 'from')
                , (NAME, 'noseOfYeti'), (OP, '.'), (NAME, 'tokeniser'), (OP, '.'), (NAME, "support")
                , (NAME, 'import'), (OP, '*')
        ])
    
    def test_extra_imports_not_added_if_no_defaults(self):
        determine_imports(with_default_imports=True, without_should_dsl=True) |should| equal_to([
              (NAME, 'import'), (NAME, 'nose'), (OP, ';')
            , (NAME, 'from'), (NAME, 'nose'), (OP, '.'), (NAME, 'tools'), (NAME, 'import'), (OP, '*'), (OP, ';')
            , (NAME, 'from')
                , (NAME, 'noseOfYeti'), (OP, '.'), (NAME, 'tokeniser'), (OP, '.'), (NAME, "support")
                , (NAME, 'import'), (OP, '*')
        ])
    
    def test_should_dsl_imports_added_if_specified(self):
        determine_imports(with_default_imports=True, without_should_dsl=False) |should| equal_to([
              (NAME, 'import'), (NAME, 'nose'), (OP, ';')
            , (NAME, 'from'), (NAME, 'nose'), (OP, '.'), (NAME, 'tools'), (NAME, 'import'), (OP, '*'), (OP, ';')
            , (NAME, 'from'), (NAME, 'should_dsl'), (NAME, 'import'), (OP, '*'), (OP, ';')
            , (NAME, 'from')
                , (NAME, 'noseOfYeti'), (OP, '.'), (NAME, 'tokeniser'), (OP, '.'), (NAME, "support")
                , (NAME, 'import'), (OP, '*')
        ])
    
    def test_it_returns_nothing_if_no_imports(self):
        determine_imports(with_default_imports=False, without_should_dsl=True) |should| equal_to([])