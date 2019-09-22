Nose of Yeti
============

This is a project to provide a Behaviour Driven Development style DSL (domain specific language) for python tests.

It uses the fact that you can register a codec that is able to modify a python file before executing it.

http://docs.python.org/library/codecs.html

Using this we can make it so that when python imports a file with a particular encoding as the first line of the file (noseOfYeti looks for ``# coding: spec``), it will be intercepted and the tokens in the file will be translated to something else before the import continues.

NoseOfYeti uses this technique to translate from the DSL it defines into python classes and functions that may be recognised by the Python Nose testing framework.

https://readthedocs.org/docs/nose/

It was originally developed by Stephen Moore after borrowing the idea from a project by Fernando Meyer called Yeti

https://github.com/fmeyer/yeti

Changelog
=========

Note that it is recommended you remove .pyc of your noseOfYeti specs when you upgrade noseOfYeti.
The python interpreter skips the translation process if it sees a .pyc file (unless the .py file has changed since the .pyc file was created).
This means that any changes in the translation process won't happen untill either the .pyc files are removed or all the .py files have been changed.

``1.9.1``
    Turns out the incremental decoder does get used for the whole file, so I've
    fixed that. But I was still able to make read the file as is if I've only
    got part of the file

``1.9.0``
    Made the incremental decoder just utf8 so that pdb inside a spec file is able
    to show lines from the test. This works because the import time translation
    doesn't use the incremental decoder. And this is necessary because the
    incremental decoder would often get confused by the indentation and return
    nothing

    Also, noseOfYeti will now detect bracket mismatches and tell you where you've
    made a mistake. I.e. if you close the wrong type of bracket, or have a
    mismatched bracket, or have a hanging open bracket, it will tell you line
    and column numbers of where this is happening

``1.8.3``
    Make pytest support __only_run_tests_in_children__ property on describes

    You can now translate a string by doing::

        from noseOfYeti.tokeniser.spec_codec import codec_from_options
        spec_codec = codec_from_options()
        translated = spec_codec.translate(src_str_or_bytes)

``1.8.2``
    Made pytest support play nicer when running against a unittest suite

``1.8.1``
    Added support for pytest.

    The support means the spec codec is registered for you and nested describes
    will not run inherited tests.

``1.8``
    Changed the license to MIT from GPL

``1.7``
    NoseOfYeti now understands and respects the async keyword.

    Only really useful if you use something like https://asynctest.readthedocs.io/en/latest/

``1.6``
    Nose2 support!

``1.5.2``
    Python3 Compatibility with the plugins

``1.5.1``
    Fixed a problem with repeating tests in sub-describes

``1.5.0``
    Added python3 support (based off the work by cwacek)

    Use tox to run tests in python2 and python3 now

    Updated pylint plugin - Unfortunately seems to cause a lot of "Final newline missing" however....

``1.4.9``
    Added __only_run_tests_in_children__ functionality

``1.4.8``
    Fixed ignore tests so they don't inject a nose.SkipTest

    Removed all reference to should_dsl (Except for the tests, I'll change those another day)

``1.4.7``
    No injected imports by default

    And changed --noy-without-should-dsl and --noy-without-default-imports to --noy-with-should-dsl and --noy-with-default-imports

``1.4.6``
    Can now set common settings in a config json file.

``1.4.4`` and ``1.4.5``
    Minor fixes

``1.4.3``
    Added wrapped-setup option to allow decorating before_each and after_each functions instead of inserting a super call into them.

``pre 1.4.3``
    No Changelog was maintained.

Docs
====

Docs can now be found using the wonderful readthedocs.org
http://readthedocs.org/docs/noseofyeti/en/latest/

Tests
=====

Always use a virtualenv!::

    # http://virtualenvwrapper.readthedocs.org/en/latest/
    $ mkvirtualenv noseOfYeti

    $ cd /root/of/noseOfYeti
    $ pip install -e .
    $ pip install "noseOfYeti[tests]"
    $ ./test.sh

Or just run tox::

    $ tox

