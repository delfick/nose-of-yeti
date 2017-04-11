from setuptools import setup
from textwrap import dedent

setup(
       name = 'noseOfYeti'
     , version = "1.7"
     , classifiers =
       [ 'Intended Audience :: Developers'
       , 'Programming Language :: Python'
       , 'Topic :: Software Development :: Documentation'
       , 'Topic :: Software Development :: Testing'
       ]

     , author = 'Stephen Moore'
     , license = 'GPL'
     , keywords = 'bdd rspec spec'
     , author_email = 'delfick755@gmail.com'

     , url = "https://github.com/delfick/nose-of-yeti"
     , description = 'Nose plugin providing BDD dsl for python'
     , long_description = dedent("""
          Plugin for nose, inspired by http://github.com/fmeyer/yeti, which uses a codec style
          to provide an RSpec style BDD dsl for python tests
       """)

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

