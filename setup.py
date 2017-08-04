#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function

import os.path
import warnings
import sys

from pip.req import parse_requirements


try:
    from setuptools import setup, Command
    setuptools_available = True
except ImportError:
    from distutils.core import setup, Command
    setuptools_available = False
from distutils.spawn import spawn

try:
    # This will create an exe that needs Microsoft Visual C++ 2008
    # Redistributable Package
    import py2exe
except ImportError:
    if len(sys.argv) >= 2 and sys.argv[1] == 'py2exe':
        print('Cannot import py2exe', file=sys.stderr)
        exit(1)

py2exe_options = {
    'bundle_files': 1,
    'compressed': 1,
    'optimize': 2,
    'dist_dir': '.',
    'dll_excludes': ['w9xpopen.exe', 'crypt32.dll'],
}

# Get the version from youtube_dl/version.py without importing the package
exec(compile(open('beaver/version.py').read(),
             'beaver/version.py', 'exec'))

DESCRIPTION = 'Tool for templated code generation'
LONG_DESCRIPTION = 'Command-line program to generate source code from a Jinja2 template and 1 or more input structures'

py2exe_console = [{
    'script': './beaver/__main__.py',
    'dest_base': 'beaver',
    'version': __version__,
    'description': DESCRIPTION,
    'comments': LONG_DESCRIPTION,
    'product_name': 'beaver',
    'product_version': __version__,
}]

py2exe_params = {
    'console': py2exe_console,
    'options': {'py2exe': py2exe_options},
    'zipfile': None
}

if len(sys.argv) >= 2 and sys.argv[1] == 'py2exe':
    params = py2exe_params
else:
    files_spec = [
    ]
    root = os.path.dirname(os.path.abspath(__file__))
    data_files = []
    for dirname, files in files_spec:
        resfiles = []
        for fn in files:
            if not os.path.exists(fn):
                warnings.warn('Skipping file %s since it is not present. Type  make  to build all automatically generated files.' % fn)
            else:
                resfiles.append(fn)
        data_files.append((dirname, resfiles))

    params = {
        'data_files': data_files,
    }
    if setuptools_available:
        params['entry_points'] = {'console_scripts': ['beaver = beaver:main']}
    else:
        params['scripts'] = ['bin/beaver']



def find_repository():
    """Find the location of devops-scripts."""
    repo_dir = os.path.expanduser(os.path.dirname(__file__))

    if not repo_dir or repo_dir == '.':
        repo_dir = os.getcwd()

    return repo_dir


repo_dir = find_repository()
requirements_file = os.path.join(
    repo_dir,
    'requirements.txt'
)
requirements = [
    str(r.req) for r in parse_requirements(
        requirements_file,
        session=False
    )
]

setup(
    author='Curtis La Graff',
    author_email='curtis@lagraff.me',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'License :: Public Domain',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description=DESCRIPTION,
    install_requires=requirements,
    long_description=LONG_DESCRIPTION,
    maintainer='Curtis La Graff',
    maintainer_email='curtis@lagraff.me',
    name='beaver',
    packages=[
        'beaver',
        'beaver.drivers',
        'beaver.cli',
    ],
    test_requires = ['nosetest'],
    test_suite = 'nose.collector',
    url='https://github.com/clagraff/beaver',
    version=__version__,
    **params
)
