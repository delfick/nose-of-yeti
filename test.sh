#!/usr/bin/env python
from noseOfYeti.plugins.nosetests import Plugin as noyPlugin
import nose
import sys

if __name__ == '__main__':
    from noseOfYeti.specs.matchers import ResultIn
    nose.main()

