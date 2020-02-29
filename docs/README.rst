Documentation
=============

To build the documentation run::

   $ ./build_docs

If you want to build from fresh then say::

   $ ./build_docs fresh

Once your documentation is built do something like::

   $ python3 -m http.server 9087

And go to http://localhost:9087/_build/html/index.html
