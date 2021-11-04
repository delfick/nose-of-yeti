from setuptools import setup, find_packages
from noseOfYeti import VERSION

# fmt: off

setup(
      name = 'noseOfYeti'
    , version = VERSION
    , packages = find_packages(include="noseOfYeti.*", exclude=["tests*"])

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
    , description = 'A custom pyton codec that provides an RSpec style dsl for python'
    , long_description = open("README.rst").read()

    , extras_require =
      { 'tests':
        [ "asynctest==0.13.0"
        , "pytest==6.2.5"
        , "alt-pytest-asyncio==0.6.0"
        , "pytest-helpers-namespace==2021.4.29"
        ]
      }

    , entry_points =
      { 'console_scripts' :
        [ 'run_noseOfYeti_tests = noseOfYeti:run_pytest'
        , 'noy_pylama = noseOfYeti.plugins.pylama:run_pylama'
        ]
      , 'nose.plugins':
        [ 'noseOfYeti = noseOfYeti.plugins.nosetests:Plugin'
        ]
      , "pytest11": ["nose_of_yeti = noseOfYeti.plugins.pytest"]
      , 'pyls': ['pyls_noy = noseOfYeti.plugins.pyls']
      }
    )

# fmt: on
