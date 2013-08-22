.. _usage:

Usage
=====

All that's needed to setup nose-of-yeti is to register the spec codec before importing the specs. Python mechanics handle the rest. Included with nose-of-yeti is plugins for nosetests and pylint for doing just this.

Nosetests
=========

After running setup.py (``easy_install .`` or ``pip install .`` or even ``pip install noseOfYeti``) you can run nosetests with ``--with-noy``, which will enable the spec codec.

see :ref:`options` for other options available.

Pylint
======

It is possible to use pylint with a noseOfYeti spec. All you have to do is add ``noseOfYeti.plugins.pylinter'`` to pylint's ``load-plugins`` option.

This plugin will register the spec codec so that it can use it to determine what is in a spec file.

The codec will also make an effort to return lines from the original file (with normalized indentation) so that you don't get too many errors about bad spacing. (codec doesn't have any control over spaces between things)

see :ref:`options` for options that are available.

Sphinx
======

You can add ``noseOfYeti.plugins.sphinx`` to sphinx' ``extensions`` option to register the spec encoding so that sphinx may successfully import your tests (i.e. for automatic documentation creation)

see :ref:`options` for options that are available.

.. _options:

Options
=======

Nosetests and pylint offer the same settings as shown below

Note that Nosetests require the settings to be prefixed by --noy; and sphinx prefixes options with noy\_ and replaces dashes with underscores.

.. spec_options::
    asdf

PyDev - Debugger
================

If you're using PyDev debugger, you are able to set breakpoints in spec files if you can patch::

    eclipse/plugins/org.python.pydev.debug_.../pysrc/pydevd_frame.py, in trace_dispatch():

        < if func_name in ('None', curr_func_name):

        > if func_name in ('None', '', curr_func_name):

