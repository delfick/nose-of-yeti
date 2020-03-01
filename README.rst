Nose of Yeti
============

This is a project creates a custom Python ``codec`` that lets you write your
tests using an RSpec inspired DSL (i.e. ``describe`` and ``it`` blocks)

It uses the fact that you can register a codec that is able to modify a Python
file before executing it.

http://docs.python.org/library/codecs.html

Using this we can make it so that when Python imports a file with a particular
encoding as the first line of the file it will be intercepted and potentially
rewritten into something else before the import continues.

nose-of-yeti uses this technique to translate from the DSL it defines, into 
Python classes and functions that then will be executed by your test framework
of choice.

It was originally developed by Stephen Moore after borrowing the idea from a
project by Fernando Meyer called Yeti

https://github.com/fmeyer/yeti

You can find documentation at http://noseofyeti.readthedocs.io and the code
over at https://github.com/delfick/nose-of-yeti

Updating nose-of-yeti version
-----------------------------

It is recommended you remove .pyc of your nose-of-yeti specs when you
upgrade nose-of-yeti. The Python interpreter skips the translation process if it
sees a .pyc file (unless the .py file has changed since the .pyc file was
created). This means that any changes in the translation process won't happen
until either the .pyc files are removed or all the .py files have been changed.
