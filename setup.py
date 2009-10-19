#!/usr/bin/env python
from distutils.core import setup

setup(
    name='mutter',
    version='0.0.2',
    description='Smart little muttering command runner',
    author='Travis cline',
    author_email='travis.cline@gmail.com',
    url='http://github.com/traviscline/mutter',
    packages=['mutter'],
    package_data={'mutter': ['sounds/*']},
    scripts=['bin/mutter'],
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: BSD License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Topic :: Utilities'],
)