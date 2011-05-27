Nose of Yeti
============

This is a project to provide a BDD style dsl for python tests.

It uses the fact that you can register a codec that is able to modify a python file before executing it.

http://docs.python.org/library/codecs.html

Using this we're able to make it so when you have "# coding: spec" at the top of the file, it will read your spec, which is in a nice dsl, and turn it into classes that can then be used by Nose.

http://somethingaboutorange.com/mrl/projects/nose/1.0.0/

It was originally developed by Stephen Moore after borrowing the idea from a project by Fernando Meyer called Yeti

https://github.com/fmeyer/yeti

Usage
=====

Look at the files in the examples directory to see what using nose-of-yeti looks like.

PyDebugger
==========

If you're using PyDev debugger, you are able to set breakpoints in spec files if you can patch::

    eclipse/plugins/org.python.pydev.debug_.../pysrc/pydevd_frame.py, in trace_dispatch():

        < if func_name in ('None', curr_func_name):

        > if func_name in ('None', '', curr_func_name):

Pinocchio - Spec Extension
==========================

There exists a patch to improve spec when using nose-of-yeti together with the pinocchio spec extension.

This patch will enable hierarchichal output of specifications, like this:

    Transaction:
      - persists its state across requests (SKIPPED)
         add command:
          - throws an error if is running is false
             when the command is invalid:
              - rejects the command with a validation error
             when the command is valid:
              - adds the command to the stack

    etc.

Please download the patch from <https://github.com/jerico-dev/pinocchio/commit/b7f76560d5664a99ed5de7315d21c4727fe5b905.patch>.
