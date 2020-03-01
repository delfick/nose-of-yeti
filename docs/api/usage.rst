.. _usage:

Usage
=====

All that's needed to setup nose-of-yeti is to register the spec codec before
importing the specs. Python mechanics handle the rest. Included with
nose-of-yeti is plugins for nosetests and pytest for doing just this.

Nosetests
---------

You need to run nosetests with the ``--with-noy`` options.

Pytests
-------

Having nose-of-yeti in your environment is enough for pytest to be able to
import spec encoded files.
