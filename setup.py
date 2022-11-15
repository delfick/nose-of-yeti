from setuptools.command.build_py import build_py
from setuptools import find_packages, setup
from noseOfYeti import VERSION
import os


class build_py_and_add_pth(build_py):
    def run(self):
        super().run()

        outfile = os.path.join(self.build_lib, "noy_black.pth")
        self.copy_file(
            os.path.join("noseOfYeti", "black", "noy_black.pth"), outfile, preserve_mode=0
        )


# fmt: off

setup(
      name = 'noseOfYeti'
    , version = VERSION
    , packages = find_packages(include="noseOfYeti.*", exclude=["tests*"])
    , package_data={'noseOfYeti': ['black/*']}
    , cmdclass={"build_py": build_py_and_add_pth}

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
        , "pytest>=7.0.1"
        , "alt-pytest-asyncio==0.6.0"
        , "pytest-helpers-namespace==2021.4.29"
        ]
       , "black":
        [ "importlib-resources==5.10.0"
        , "black==22.10.0"
        ]
      }

    , entry_points =
      { 'pylama.linter':
        [ 'pylama_noy = noseOfYeti.plugins.pylama:Linter'
        ]
      , 'nose.plugins':
        [ 'noseOfYeti = noseOfYeti.plugins.nosetests:Plugin'
        ]
      , "pytest11": ["nose_of_yeti = noseOfYeti.plugins.pytest"]
      , 'pyls': ['pyls_noy = noseOfYeti.plugins.pyls']
      }
    )

# fmt: on
