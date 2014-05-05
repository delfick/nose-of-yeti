from should_dsl import should
import fudge

from noseOfYeti.tokeniser.config import Default, ConfigUtil, MissingConfigFile
from .helpers import a_temp_file

# Silencing code checker about should_dsl matchers
be = None
throw = None
equal_to = None

def test_config_util_initialisation():
    '''Test ConfigUtil initialises properly'''
    template = fudge.Fake("template")
    config_util = ConfigUtil(template)

    config_util.values |should| equal_to({})
    config_util.template |should| be(template)

def test_config_util_normalising_keys():
    '''Test ConfigUtil knows how to normalise a key'''
    config_util = ConfigUtil()
    config_util.normalise_key("blah") |should| equal_to("blah")
    config_util.normalise_key("blah_stuff-things") |should| equal_to("blah_stuff_things")
    config_util.normalise_key("blah-stuff-things") |should| equal_to("blah_stuff_things")

class Test_ConfigUtil_FindingValue(object):
    '''Make sure we can find a value'''
    def test_it_raises_attributeError_when_key_doesnt_exist(self):
        config_util = ConfigUtil()
        config_util.values = {"a":1}

        config_util.find_value("a") |should| be(1)

        finder = lambda : config_util.find_value("b")
        finder |should| throw(AttributeError, "Config has no value for b")

    def test_it_returns_actual_value_if_finds_default(self):
        config_util = ConfigUtil()
        config_util.values = {"a":Default(21)}
        config_util.find_value("a") |should| be(21)

    def test_it_returns_value_as_is(self):
        val = fudge.Fake("val")
        config_util = ConfigUtil()
        config_util.values = {"c":val}
        config_util.find_value("c") |should| be(val)

class Test_ConfigUtil_UsingOptions(object):
    '''Make sure it knows how to use options'''
    def setup(self):
        self.config_util = ConfigUtil()
        self.config_util.values |should| equal_to({})

    def test_it_puts_options_in_values(self):
        self.config_util.use_options({"a":1, "b":2})
        self.config_util.values |should| equal_to({"a":1, "b":2})

    def test_it_overrides_all_values(self):
        c_val = Default(3)
        self.config_util.use_options({"a":1, "b":2, "c":c_val})
        self.config_util.values |should| equal_to({"a":1, "b":2, "c":c_val})

        self.config_util.use_options({"b":4, "c":5, "d":6})
        self.config_util.values |should| equal_to({"a":1, "b":4, "c":5, "d":6})

    def test_it_normalises_keys(self):
        self.config_util.use_options({"a-b":1, "c_d":2, "e-f_g-h":3})
        self.config_util.values |should| equal_to({"a_b":1, "c_d":2, "e_f_g_h":3})

    def test_it_uses_extractor_if_provided(self):
        template = fudge.Fake("template")
        def extractor(templ, values):
            templ |should| be(template)
            for key, val in values.items():
                yield "e-{}".format(key), val + 1

        self.config_util.template = template
        self.config_util.use_options({"a":1, "b":2, "c":3}, extractor=extractor)
        self.config_util.values |should| equal_to({"e_a":2, "e_b":3, "e_c":4})

    def test_it_works_with_list_of_tuples(self):
        c_val = Default(3)
        self.config_util.use_options([("a",1), ("b",2), ("c",c_val)])
        self.config_util.values |should| equal_to({"a":1, "b":2, "c":c_val})

    def test_it_doesnt_complain_if_extractor_returns_none(self):
        '''It's valid for the extractor to say there are no values'''
        template = fudge.Fake("template")
        def extractor(templ, values):
            templ |should| be(template)
            return None

        self.config_util.template = template
        self.config_util.use_options({"a":1, "b":2, "c":3}, extractor=extractor)
        self.config_util.values |should| equal_to({})

class Test_ConfigUtil_FindingConfigFile(object):
    '''Test that the ConfigUtil class knows corner cases of finding a config file'''
    def setUp(self):
        self.config_util = ConfigUtil()
        self.fullpath = fudge.Fake('fullpath')
        self.filename = fudge.Fake('filename')

    @fudge.patch('os.path.exists', 'os.path.abspath')
    def test_it_complains_if_config_file_doesnt_exist(self, fake_exists, fake_abspath):
        self.config_util.values['config_file'] = self.filename
        fake_abspath.expects_call().with_args(self.filename).returns(self.fullpath)
        fake_exists.expects_call().with_args(self.fullpath).returns(False)

        finder = lambda : self.config_util.find_config_file()
        finder |should| throw(MissingConfigFile, "Config file doesn't exist at fake:fullpath")

    @fudge.patch('os.path.exists', 'os.path.abspath')
    def test_it_defaults_to_noyjson(self, fake_exists, fake_abspath):
        fake_abspath.expects_call().with_args('noy.json').returns(self.fullpath)
        fake_exists.expects_call().with_args(self.fullpath).returns(True)
        self.config_util.find_config_file() |should| equal_to(self.fullpath)

    @fudge.patch('os.path.exists', 'os.path.abspath')
    def test_it_doesnt_care_if_default_doesnt_exist(self, fake_exists, fake_abspath):
        fake_abspath.expects_call().with_args('noy.json').returns(self.fullpath)
        fake_exists.expects_call().with_args(self.fullpath).returns(False)
        self.config_util.find_config_file() |should| equal_to(None)

    @fudge.patch('os.path.exists', 'os.path.abspath')
    def test_it_doesnt_care_if_provided_default_doesnt_exist(self, fake_exists, fake_abspath):
        self.config_util.values['config_file'] = Default(self.filename)
        fake_abspath.expects_call().with_args(self.filename).returns(self.fullpath)
        fake_exists.expects_call().with_args(self.fullpath).returns(False)
        self.config_util.find_config_file() |should| equal_to(None)

class Test_ConfigUtil_ApplyingConfigFile(object):
    '''Make sure it knows what values from the config file to apply'''
    def test_it_sets_options_from_an_json_file(self):
        contents = """
            { "a" : "stuff"
            , "b" : "things"
            }
        """
        with a_temp_file(contents) as filename:
            config_util = ConfigUtil()
            config_util.values |should| equal_to({})
            config_util.apply_config_file(filename)
            config_util.values |should| equal_to({"a":"stuff", "b":"things"})

    def test_it_doesnt_override_existing_non_default_values(self):
        contents = """
            { "a" : "stuff"
            , "b" : "things"
            , "c" : "and"
            , "d" : "shells"
            , "e-f" : "blah"
            , "g-h" : "other"
            }
        """
        with a_temp_file(contents) as filename:
            config_util = ConfigUtil()
            c_val = Default(21)
            config_util.use_options({'b':21, 'c':c_val, 'd':None, "g-h":"meh"})
            config_util.values |should| equal_to({'b':21, 'c':c_val, 'd':None, "g_h":"meh"})

            config_util.apply_config_file(filename)
            config_util.values |should| equal_to({"a":"stuff", "b":21, "c":"and", 'd':None, "e_f":"blah", "g_h":"meh"})

class Test_ConfigUtil_UsingConfigFile(object):
    '''Make sure it knows how to find and apply a config file'''
    @fudge.test
    def test_it_doesnt_care_if_no_config_file(self):
        config_util = ConfigUtil()
        fake_find_config_file = fudge.Fake("find_config_file").expects_call().returns(None)
        fake_apply_config_file = fudge.Fake("apply_config_file")

        with fudge.patched_context(config_util, 'find_config_file', fake_find_config_file):
            with fudge.patched_context(config_util, 'apply_config_file', fake_apply_config_file):
                config_util.use_config_file()

    @fudge.test
    def test_it_applies_config_file_if_one_is_found(self):
        config_util = ConfigUtil()
        config_file = fudge.Fake("config_file")
        fake_find_config_file = fudge.Fake("find_config_file").expects_call().returns(config_file)
        fake_apply_config_file = fudge.Fake("apply_config_file").expects_call().with_args(config_file)

        with fudge.patched_context(config_util, 'find_config_file', fake_find_config_file):
            with fudge.patched_context(config_util, 'apply_config_file', fake_apply_config_file):
                config_util.use_config_file()

