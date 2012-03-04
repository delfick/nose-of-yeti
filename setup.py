from setuptools import setup

setup( name='noseOfYeti'
     , version="1.0"
     , classifiers=[ 'Intended Audience :: Developers'
                   , 'Programming Language :: Python'
                   , 'Topic :: Software Development :: Documentation'
                   , 'Topic :: Software Development :: Testing'
                   ]
                   
     , keywords='bdd rspec spec'
     , author = 'Stephen Moore'
     , author_email = 'delfick755@gmail.com'
     , license = 'GPL'

     , description = 'Nose plugin providing BDD dsl for python'
     , long_description = """\
Plugin for nose, inspired by http://github.com/fmeyer/yeti, which uses a codec style
to provide an RSpec style BDD dsl for python tests
"""
     , install_requires = [ 'setuptools'
                          , 'should-dsl'
                          , 'nose'
                          ]
                          
     , packages = ['noseOfYeti']
     , entry_points = {
        'nose.plugins': [
            'noseOfYeti = noseOfYeti.plugin:Plugin'
            ]
       }
)

