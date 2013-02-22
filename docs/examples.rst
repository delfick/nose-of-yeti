.. _examples:

Examples
========

As found in the example directory:

Comparison
----------

The way nose-of-yeti works is when a file with the necessary codec is imported, it will be translated into python code before being executed. This has the nice side effect that using a nose-of-yeti spec is transparently handled via python mechanisms, and once you have a .pyc file, it doesn't need to do the translation again (untill you either delete the .pyc or change the file).

To tell python to use the correct encoding, you first let nose-of-yeti register it's codec (it comes with a plugin for both nose and pylint for this) and then you have ``# coding: spec`` as the first line of the file.

.. literalinclude:: ../example/comparison.py
   :language: python

Another Example
---------------

.. literalinclude:: ../example/test.py
   :language: python

