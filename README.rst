Nose of Yeti
============

This is a project creates a custom Python ``codec`` that lets the developer write
their tests using an `RSpec <https://rspec.info>`_ inspired DSL (i.e. ``describe``
and ``it`` blocks).

It uses the fact that python allows the registration of a
`codec <http://docs.python.org/library/codecs.html>`_ that can be used
to read in source code and modify it at import time.

NoseOfYeti uses this technique to find files with a particular coding declaration
on the first line of a file to turn the rspec inspired DSL into ordinary python
that is then executed as if it were written like that in the first place.

The original idea comes from `@fmeyer <https://github.com/fmeyer>`_ who wrote this
`blog post <https://web.archive.org/web/20120405004819/http://fmeyer.org/en/writing-a-DSL-with-python.html>`_
and a simple `proof of concept <https://github.com/fmeyer/pydsl>`_ before it was
picked up and worked on by `@hltbra <https://github.com/hltbra>`_
in `this repo <https://github.com/fmeyer/yeti>`_.

`@delfick <https://github.com/delfick>`_ discovered this work in 2010 and over the
following decade plus has improved on the concept, giving it more features and
integration with python tooling.

The documentation can be found at http://noseofyeti.readthedocs.io and the code
over at https://github.com/delfick/nose-of-yeti.

Updating nose-of-yeti version
-----------------------------

It is recommended any .pyc files are removed when NoseOfYeti is upgraded.

The Python interpreter skips the translation process if it
sees a .pyc file (unless the .py file has changed since the .pyc file was
created). This means that any changes in the translation process won't apply
until either the .pyc files are removed or all the .py files have been changed.
