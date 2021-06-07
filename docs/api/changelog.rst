.. _changelog:

Changelog
=========

.. _release-2-0-2:

2.0.2 - 22 November 2020
    * Make this work with python3.9

.. _release-2-0-1:

2.0.1 - 13 April 2020
    * Added a pyls plugin
    * Made available a ``noy_pylama`` console script to run pylama with the
      ability to translate ``coding: spec`` files

.. _release-2-0-0:

2.0.0 - 8 March 2020
    * nose-of-yeti is now only python3.6+ compatible
    * Removed support for nose2, pylint and sphinx.

      * I don't use these and I'm not sure these plugins actually work.

    * Removed configurability as I believe all the options are unnecessary.
    * ``noseOfYeti.tokeniser.register_from_options`` is now
      ``noseOfYeti.tokeniser.register``
    * Removed ``noseOfYeti.tokeniser.config``,
      ``noseOfYeti.tokeniser.imports`` and
      ``noseOfYeti.plugins.support.spec_options``
    * It is no longer valid to end an ``it`` or ``ignore`` block without a colon.
      Previously it would replace these with a line that raises nose.SkipTest.
      This obviously won't work in a non nosetests environment and I think it's
      best if skipped tests were explicit rather than injected when you forget
      a ``:``.
    * Removed the ``context`` block. Groups can now only be a ``describe``.
    * Removed wrapped setup/teardown helpers
    * You no longer need to import sync and async ``noy_sup_setUp`` or
      ``noy_sup_tearDown`` methods anymore.
    * ``noseOfYeti.plugins.support.test_chooser`` is now
      ``noseOfYeti.tokeniser.chooser``
    * Improved how I turn sentences into valid python variable names for classes
      and functions.

.. _release-1-9-1:

1.9.1 - 22 September 2019
    Turns out the incremental decoder does get used for the whole file, so I've
    fixed that. But I was still able to make read the file as is if I've only
    got part of the file

.. _release-1-9-0:

1.9.0 - 22 September 2019
    Made the incremental decoder just utf8 so that pdb inside a spec file is able
    to show lines from the test. This works because the import time translation
    doesn't use the incremental decoder. And this is necessary because the
    incremental decoder would often get confused by the indentation and return
    nothing

    Also, nose-of-yeti will now detect bracket mismatches and tell you where
    you've made a mistake. I.e. if you close the wrong type of bracket, or have
    a mismatched bracket, or have a hanging open bracket, it will tell you line
    and column numbers of where this is happening

.. _release-1-8-3:

1.8.3 - 31 August 2019
    Make pytest support __only_run_tests_in_children__ property on describes

    You can now translate a string by doing::

        from noseOfYeti.tokeniser.spec_codec import codec_from_options
        spec_codec = codec_from_options()
        translated = spec_codec.translate(src_str_or_bytes)

.. _release-1-8-2:

1.8.2 - 25 August 2019
    Made pytest support play nicer when running against a unittest suite

.. _release-1-8-1:

1.8.1 - 4 August 2019
    Added support for pytest.

    The support means the spec codec is registered for you and nested describes
    will not run inherited tests.

.. _release-1-8:

1.8 - 30 October 2018
    Changed the license to MIT from GPL

.. _release-1-7:

1.7 - 11 April 2017
    NoseOfYeti now understands and respects the async keyword.

    Only really useful if you use something like https://asynctest.readthedocs.io/en/latest/

.. _release-1-6:

1.6 - 22 July 2016
    Nose2 support!

.. _release-1-5.2:

1.5.2 - 26 May 2016
    Python3 Compatibility with the plugins

.. _release-1-5.1:

1.5.1 - 1 June 2014
    Fixed a problem with repeating tests in sub-describes

.. _release-1-5.0:

1.5.0 - 6 May 2014
    Added python3 support (based off the work by cwacek)

    Use tox to run tests in python2 and python3 now

    Updated pylint plugin - Unfortunately seems to cause a lot of
    "Final newline missing" however.

.. _release-1-4.9:

1.4.9 - 9 March 2014
    Added __only_run_tests_in_children__ functionality

.. _release-1-4.8:

1.4.8 - 22 August 2013
    Fixed ignore tests so they don't inject a nose.SkipTest

    Removed all reference to should_dsl (Except for the tests, I'll change
    those another day)

.. _release-1-4.7:

1.4.7 - 3 May 2013
    No injected imports by default

    And changed --noy-without-should-dsl and --noy-without-default-imports to
    --noy-with-should-dsl and --noy-with-default-imports

.. _release-1-4.6:

1.4.6 - 3 May 2013
    Can now set common settings in a config json file.

.. _release-1-4.5:

1.4.5 - 29 March 2013
    Minor fixes

.. _release-1-4.4:

1.4.4 - 29 August 2012
    Minor fixes

.. _release-1-4.3:

1.4.3 - 12 May 2012
    Added wrapped-setup option to allow decorating before_each and after_each
    functions instead of inserting a super call into them.

pre 1.4.3
    No Changelog was maintained.

First commit - 1 July 2010
