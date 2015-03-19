# -*- coding: utf-8 -*-
"""
Created on:    Nov 1, 2013
@author:        vahid
"""

from setuptools import setup, find_packages
import os.path
import re

# reading package's version (same way sqlalchemy does)
with open(os.path.join(os.path.dirname(__file__), 'maryjane', '__init__.py')) as v_file:
    package_version = re.compile(r".*__version__ = '(.*?)'", re.S).match(v_file.read()).group(1)

long_description = """
`MaryJane` is a Python automatic file merge tool.
Docs at http://github.com/pylover/maryjane.
"""

setup(
    name='maryjane',
    version=package_version,
    author='Vahid Mardani',
    author_email='vahid.mardani@gmail.com',
    url='http://github.com/pylover/MaryJane',
    description='Python file watcher and task manager',
    long_description=long_description,
    license='MIT',
    install_requires=['mako',
                      'pyyaml',
                      'watchdog>=0.6.0'],
    packages=['maryjane', 'maryjane.tags'],
    entry_points={
        'console_scripts': [
            'maryjane = maryjane.cli:cli_main'
        ]
    },
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
