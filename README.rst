Nose of Yeti
============

This is a project to provide a BDD style dsl for python tests.

It uses the fact that you can register a codec that is able to modify a python file before executing it.

http://docs.python.org/library/codecs.html

Using this we're able to make it so when you have "# coding: spec" at the top of the file, it will read your spec, which is in a nice dsl, and turn it into classes that can then be used by Nose.

http://somethingaboutorange.com/mrl/projects/nose/1.0.0/

It was originally developed by Stephen Moore after borrowing the idea from a project by Fernando Meyer called Yeti

https://github.com/fmeyer/yeti

Docs
====

Docs can now be found using the wonderful readthedocs.org
http://readthedocs.org/docs/noseofyeti/en/latest/