.. _examples:

Example
=======

The way nose-of-yeti works is when a file with the necessary codec is imported,
it will be translated into python code before being executed. To tell python
to use the correct encoding, you first let nose-of-yeti register its codec and
then you put a ``# coding: spec`` as the first line of the file before that
file is imported.

What you write
--------------

.. literalinclude:: ../../example/test.py
   :language: python

What python executes
--------------------

.. literalinclude:: ../../example/converted.test.py
   :language: python

.. note:: The weird spaces is because of the way Python turns the tokens into
    code when we rewrite the file at import time.
