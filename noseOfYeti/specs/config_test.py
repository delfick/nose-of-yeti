from should_dsl import should
import fudge

from noseOfYeti.tokeniser.config import Default, Config
from .helpers import a_temp_file

import six

# Silencing code checker about should_dsl matchers
be = None
equal_to = None

class Test_Default(object):

    def test_stringify_returns_value(self):
        str(Default("blah")) |should| equal_to("blah")
        if six.PY2:
            unicode(Default("blah")) |should| equal_to("blah")

        str(Default(1)) |should| equal_to("1")
        if six.PY2:
            unicode(Default(1)) |should| equal_to("1")

        class Special(object):
            def __unicode__(self):
                return 'things'
            def __str__(self):
                return 'stuff'
        str(Default(Special())) |should| equal_to("stuff")
        if six.PY2:
            unicode(Default(Special())) |should| equal_to("things")

class Test_ConfigSetup(object):
    '''Test that the Config class knows how to setup itself'''
    def test_it_updates_values_with_options(self):
        # With no values to begin with
        config = Config()
        config._util.values |should| equal_to({})
        config.setup({'a':1, 'b':2})
        config._util.values |should| equal_to({'a':1, 'b':2})

    def test_it_uses_extractor_if_provided(self):
        '''If given an extractor, it applies extractor to the options before setting them'''
        template = fudge.Fake("template")
        def extractor(template, options):
            for key, val in options.items():
                yield key, val + 1

        config = Config(template)
        config.setup({'a':1, 'b':2}, extractor=extractor)
        config._util.values |should| equal_to({'a':2, 'b':3})

    def test_it_gets_values_from_config_file(self):
        '''It gets values from a config file'''
        contents = """
            { "a" : 1
            , "b" : 2
            }
        """
        with a_temp_file(contents) as filename:
            config = Config()
            config.setup({"config-file":filename})
            config._util.values |should| equal_to({"config_file":filename, u"a":1, u"b":2})

    def test_it_overwrites_config_file_with_options(self):
        '''It gets values from a config file'''
        contents = """
            { "a" : 1
            , "b" : 2
            }
        """
        with a_temp_file(contents) as filename:
            config = Config()
            config.setup({"config-file":filename, "a":4})
            config._util.values |should| equal_to({"config_file":filename, "a":4, u"b":2})

    @fudge.patch("noseOfYeti.tokeniser.config.ConfigUtil")
    def test_setup_uses_util(self, FakeConfigUtil):
        '''It uses self._util in setup'''
        options = fudge.Fake("options")
        template = fudge.Fake("template")
        extractor = fudge.Fake("extractor")
        util = (fudge.Fake("util").remember_order()
            .expects("use_options").with_args(options, extractor)
            .expects("use_config_file")
            )

        FakeConfigUtil.expects_call().with_args(template).returns(util)
        config = Config(template)
        config.setup(options, extractor=extractor)

class Test_ConfigAttributes(object):
    '''Make sure you can get values from config like they were attributes'''

    def test_config_gets_values_like_attributes(self):
        '''Make sure the options we set can be retrieved like values'''
        config = Config()
        config.setup({"a":1, "b":2, "c-d":3})

        config.a |should| be(1)
        config.b |should| be(2)
        config.c_d |should| be(3)

    @fudge.test
    def test_config_gets_attributes_from_util(self):
        '''__getattr__ on Config uses values from util'''
        key = 'my_awesome_key'
        val = fudge.Fake("val")

        util = fudge.Fake("util").expects("find_value").with_args(key).returns(val)
        config = Config()
        config._util = util

        getattr(config, key) |should| be(val)

