# -*- coding: utf-8 -*-
'''
Created on:    Nov 1, 2013
@author:        vahid
'''

from setuptools import setup
import os.path
import re

# reading isass version (same way sqlalchemy does)
with open(os.path.join(os.path.dirname(__file__), 'maryjane', '__init__.py')) as v_file:
    package_version = re.compile(r".*__version__ = '(.*?)'", re.S).match(v_file.read()).group(1)

long_description = \
"""`MaryJane` is a Python automatic file merge tool.

Docs at http://github.com/pylover/maryjane.
"""

setup(
    name='maryjane',
    version=package_version,
    author='Vahid Mardani',
    author_email='vahid.mardani@gmail.com',
    url='http://github.com/pylover/maryjane',
    description='Python automatic file merge tool',
    long_description=long_description,
    license='MIT',
    install_requires=['pymlconf>=0.3.9',
                      'watchdog>=0.6.0'],
    packages=['maryjane'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Communications :: Email',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        ],    
    )