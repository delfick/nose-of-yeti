#!/usr/bin/env python
from noseOfYeti.plugins.nosetests import Plugin as noyPlugin
import nose
import sys

if __name__ == '__main__':
    args = sys.argv
    args.extend(['--with-noy'])
    nose.main(addplugins=[noyPlugin()], argv=args)

