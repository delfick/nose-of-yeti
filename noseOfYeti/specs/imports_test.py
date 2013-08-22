from noseOfYeti.tokeniser.imports import determine_imports
from should_dsl import should
from tokenize import NAME, OP

# Silencing code checker about should_dsl matchers
equal_to = None

class Test_DetermineImports(object):
    def test_extra_imports_are_added(self):
        extra_imports = "import thing; import stuff"
        determine_imports(
            extra_imports=extra_imports, with_default_imports=False
        ) |should| equal_to([
            (NAME, 'import'), (NAME, 'thing'), (OP, ';'), (NAME, 'import'), (NAME, 'stuff')
        ])

    def test_extra_imports_added_before_defaults(self):
        extra_imports = "import thing; import stuff"
        determine_imports(
            extra_imports=extra_imports, with_default_imports=True
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
        determine_imports(with_default_imports=True) |should| equal_to([
              (NAME, 'import'), (NAME, 'nose'), (OP, ';')
            , (NAME, 'from'), (NAME, 'nose'), (OP, '.'), (NAME, 'tools'), (NAME, 'import'), (OP, '*'), (OP, ';')
            , (NAME, 'from')
                , (NAME, 'noseOfYeti'), (OP, '.'), (NAME, 'tokeniser'), (OP, '.'), (NAME, "support")
                , (NAME, 'import'), (OP, '*')
        ])

    def test_it_returns_nothing_if_no_imports(self):
        determine_imports(with_default_imports=False) |should| equal_to([])

