import json
import os

class MissingConfigFile(Exception): pass

########################
###   DEFAULT
########################

class Default(object):
    """
        Wrapper for default values
        So we can tell the difference between default and no value
    """
    def __init__(self, val):
        self.val = val

    def __str__(self):
        return str(self.val)

    def __unicode__(self):
        return unicode(self.val)

    def append(self, val):
        """Make sure argparse doesn't fail"""
        self.val.append(val)

########################
###   CONFIGUTIL
########################

class ConfigUtil(object):
    """Config functionality"""
    def __init__(self, template=None):
        self.values = {}
        self.template = template

    def normalise_key(self, key):
        """Make sure key is a valid python attribute"""
        key = key.replace('-', '_')
        if key.startswith("noy_"):
            key = key[4:]
        return key

    def find_value(self, key):
        """Find a value and return it"""
        values = self.values
        if key not in values:
            raise AttributeError("Config has no value for {}".format(key))

        val = values[key]
        if isinstance(val, Default):
            return val.val
        else:
            return val

    def use_options(self, options, extractor=None):
        """
            If extractor isn't specified, then just update self.values with options.

            Otherwise update values with whatever the result of calling extractor with
            our template and these options returns

            Also make sure all keys are transformed into valid python attribute names
        """
        # Extract if necessary
        if not extractor:
            extracted = options
        else:
            extracted = extractor(self.template, options)

        # Get values as [(key, val), ...]
        if isinstance(extracted, dict):
            extracted = extracted.items()

        # Add our values if there are any
        # Normalising the keys as we go along
        if extracted is not None:
            for key, val in extracted:
                self.values[self.normalise_key(key)] = val

    def find_config_file(self):
        """
            Find where our config file is if there is any

            If the value for the config file is a default and it doesn't exist
            then it is silently ignored.

            If however, the value isn't a default and it doesn't exist, an error is raised
        """
        filename = self.values.get('config_file', Default('noy.json'))

        ignore_missing = False
        if isinstance(filename, Default):
            filename = filename.val
            ignore_missing = True

        filename = os.path.abspath(filename)
        if os.path.exists(filename):
            return filename
        elif not ignore_missing:
            raise MissingConfigFile("Config file doesn't exist at {}".format(filename))

    def apply_config_file(self, filename):
        """
            Add options from config file to self.values
            Leave alone existing values that are not an instance of Default
        """
        def extractor(template, options):
            """Ignore things that are existing non default values"""
            for name, val in options:
                normalised = self.normalise_key(name)
                if normalised in self.values and not isinstance(self.values[normalised], Default):
                    continue
                else:
                    yield name, val

        items = json.load(open(filename)).items()
        self.use_options(items, extractor)

    def use_config_file(self):
        """Find and apply the config file"""
        self.config_file = self.find_config_file()
        if self.config_file:
            self.apply_config_file(self.config_file)

########################
###   CONFIG
########################

class Config(object):
    """
        A wrapper around ConfigUtil.

        This provides a setup function that knows how to initialise from some options
        And how to find a config file and apply those values
        (config file values are overwritten by the options passed into setup)

        It then provides a __getattr__ to access the values on the ConfigUtil.
    """
    def __init__(self, template=None):
        self._util = ConfigUtil(template)

    def setup(self, options=None, extractor=None):
        """
            Put options onto the config and put anything from a config file onto the config.

            If extractor is specified, it is used to extract values from the options dictionary
        """
        # Get our programmatic options
        self._util.use_options(options, extractor)

        # Overwrite non defaults in self.values with values from config
        self._util.use_config_file()

    def __getattr__(self, key):
        """Get us attributes from the class or from self.values"""
        if key.startswith("_") or key in self.__dict__:
            return object.__getattribute__(self, key)

        return self._util.find_value(key)

