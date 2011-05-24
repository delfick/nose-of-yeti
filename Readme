Nose of Yeti
============

This is a project to provide a BDD style dsl for python tests.

It uses the fact that you can register a codec that is able to modify a python file before executing it.
http://docs.python.org/library/codecs.html

Using this we're able to make it so when you have "# coding: spec" at the top of the file, it will read your spec, which is in a nice dsl, and turn it into classes that can then be used by Nose.
http://somethingaboutorange.com/mrl/projects/nose/1.0.0/

It was originally developed by Stephen Moore after borrowing the idea from a project by Fernando Meyer called Yeti (https://github.com/fmeyer/yeti)

Usage
=====

Look at the files in the usage directory to see what using nose-of-yeti looks like.

PyDebugger
==========

if you're using PyDev debugger, you are able to set breakpoints in spec files if you can patch:

eclipse/plugins/org.python.pydev.debug_.../pysrc/pydevd_frame.py, in trace_dispatch():

    < if func_name in ('None', curr_func_name):

    > if func_name in ('None', '', curr_func_name):
