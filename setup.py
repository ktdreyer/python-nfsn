import sys
import re
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

module_file = open('nfsn/__init__.py').read()
metadata = dict(re.findall("__([a-z]+)__\s*=\s*'([^']+)'", module_file))

class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ''

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main('nfsn/tests ' + self.pytest_args)
        sys.exit(errno)

setup(name='python-nfsn',
      version=metadata['version'],
      description=("Interact with NearlyFreeSpeech's API"),
      classifiers=['Development Status :: 4 - Beta',
                   'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   ],
      keywords='nearlyfreespeech.net',
      author='ken dreyer',
      author_email='ktdreyer [at] ktdreyer [dot] com',
      url='https://github.com/ktdreyer/python-nfsn',
      license='License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
      packages=find_packages(),
      install_requires=[
          'beanbag',
          'requests',
      ],
      entry_points={
        'console_scripts': [
            'pynfsn = nfsn.cli:main',
            ],
      },
      tests_require=[
          'beanbag',
          'httpretty',
          'pytest',
          'requests',
      ],
      cmdclass = {'test': PyTest},
)
