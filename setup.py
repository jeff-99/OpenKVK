from __future__ import print_function
import io
import os
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand

import OpenKVK


here = os.path.abspath(os.path.dirname(__file__))

def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.md', 'CHANGES.md')

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

setup(
    name='OpenKVK',
    version=OpenKVK.__version__,
    url='http://github.com/jeff99/OpenKVK',
    license='Apache Software License',
    author='Jeff Slort',
    tests_require=['pytest'],
    install_requires=[''],
    cmdclass={'test': PyTest},
    author_email='OpenKVK@jeffreyslort.nl',
    description='Python API wrapper voor de OpenKVK service',
    long_description=long_description,
    packages=['OpenKVK'],
    include_package_data=True,
    platforms='any',
    test_suite='OpenKVK.test.test_openkvk',
    classifiers = [
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Natural Language :: Nederlands',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        ],
    extras_require={
        'testing': ['pytest'],
    }
)
