from noseOfYeti import VERSION
from setuptools import setup
from textwrap import dedent

setup(
       name = 'noseOfYeti'
     , version = VERSION
     , classifiers =
       [ 'Intended Audience :: Developers'
       , 'Programming Language :: Python'
       , 'Topic :: Software Development :: Documentation'
       , 'Topic :: Software Development :: Testing'
       ]

     , author = 'Stephen Moore'
     , license = 'MIT'
     , keywords = 'bdd rspec spec'
     , author_email = 'delfick755@gmail.com'

     , url = "https://github.com/delfick/nose-of-yeti"
     , description = 'Nose plugin providing BDD dsl for python'
     , long_description = open("README.rst").read()

     , extras_require =
       { 'tests':
         [ 'nose'
         , 'fudge'
         , 'should-dsl'
         ]
       , 'docs':
         [ 'nose'
         , 'fudge'
         , 'sphinx'
         , 'pinocchio'
         , 'should_dsl'
         ]
       }

     , install_requires =
       [ 'six'
       ]

     , packages =
       [ 'noseOfYeti'
       , 'noseOfYeti.specs'
       , 'noseOfYeti.plugins'
       , 'noseOfYeti.tokeniser'
       , 'noseOfYeti.plugins.support'
       ]

     , entry_points =
       { 'nose.plugins':
         [ 'noseOfYeti = noseOfYeti.plugins.nosetests:Plugin'
         ]
       }
     )
