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

You may tell pylama to use the ``pylama_noy`` linter to make pylama aware of
``spec`` encoded files. Make sure it is defined before other linters!

It is also recommended adding to pylama configuration::

    [pylama:tests*]
    ignore = E225,E202,E211,E231,E226,W292,W291,E251,E122,E501,E701,E227,E305,E128,E228,E203,E261

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
