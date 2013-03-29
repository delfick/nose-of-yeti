Nose of Yeti
============

This is a project to provide a Behaviour Driven Development style DSL (domain specific language) for python tests.

It uses the fact that you can register a codec that is able to modify a python file before executing it.

http://docs.python.org/library/codecs.html

Using this we can make it so that when python imports a file with a particular encoding as the first line of the file (noseOfYeti looks for ``# coding: spec``), it will be intercepted and the tokens in the file will be translated to something else before the import continues.

NoseOfYeti uses this technique to translate from the DSL it defines into python classes and functions that may be recognised by the Python Nose testing framework.

http://somethingaboutorange.com/mrl/projects/nose/1.0.0/

It was originally developed by Stephen Moore after borrowing the idea from a project by Fernando Meyer called Yeti

https://github.com/fmeyer/yeti

Changelog
=========

Note that it is recommended you remove .pyc of your noseOfYeti specs when you upgrade noseOfYeti.
The python interpreter skips the translation process if it sees a .pyc file (unless the .py file has changed since the .pyc file was created).
This means that any changes in the translation process won't happen untill either the .pyc files are removed or all the .py files have been changed.

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

