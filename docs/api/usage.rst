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

Pyls
----

You can make python language server not complain about ``coding: spec`` files
by including configuration for pyls that looks like:

.. code-block:: json

    "pyls": {
      "plugins": {
        "noy_pyls": {
          "enabled": true
        }
      }
    }

Pylama
------

Pylama doesn't understand ``coding: spec`` files, but noseOfYeti makes available
a ``noy_pylama`` command that you can use instead that will translate files
that start with ``# coding: spec``.

Black
-----

To format files with the ``spec`` encoding you need to use a specific version of black
that isn't installed as a binary and have a specific environment variable set::

    > pip uninstall black
    > pip install --no-binary black noseOfYeti[black]
    > NOSE_OF_YETI_BLACK_COMPAT=true black .

MyPy
----

Add this to your mypy `configuration <https://mypy.readthedocs.io/en/stable/config_file.html#config-file>`_::

    [mypy]
    plugins = noseOfYeti.plugins.mypy

Note that if you choose to put this in ``pyproject.toml`` it should look like::

    [tool.mypy]
    plugins = 'noseOfYeti.plugins.mypy'
