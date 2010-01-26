# Copyright (C) 2008-2009 Open Society Institute
#               Thomas Moroz: tmoroz@sorosny.org
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License Version 2 as published
# by the Free Software Foundation.  You may not use, modify or distribute
# this program under any other version of the GNU General Public License.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

__version__ = '3.16dev'

import os

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.txt')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = ''
    CHANGES = ''

requires = [
    'coverage',
    'feedparser',
    'FormEncode',
    'icalendar',
    'lxml',
    'markdown2',
    'PILwoTk',
    'nose',
    'repoze.bfg >= 1.2a6',
    'repoze.browserid',
    'repoze.catalog',
    'repoze.enformed',
    'repoze.evolution',
    'repoze.folder',
    'repoze.lemonade',
    'repoze.mailin',
    'repoze.mailin.monitor',
    'repoze.monty',
    'repoze.retry',
    'repoze.sendmail',
    'repoze.session',
    'repoze.tm2',
    'repoze.who',
    'repoze.whoplugins.zodb',
    'repoze.workflow',
    'repoze.zodbconn',
    'setuptools',
    'simplejson',
    'twill', # for testing
    'ZODB3',
    'zope.testing', # fwd compat when not directly relied on by BFG
    'PILwoTk',
    'icalendar',
    'markdown2',
    'repoze.bfg.formish',
    'twill', # for testing
    # Not really a code depdencency, but used by most buildouts
    # XXX Move to eggs in buildout?
    'repoze.errorlog',
    'supervisor',
]

setup(name='karl',
      version=__version__,
      description='karl',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg zope',
      packages=find_packages(),
      include_package_data=True,
      namespace_packages = ['karl'],
      zip_safe=False,
      install_requires = requires,
      tests_require = requires,
      test_suite="karl",
      entry_points = """\
      [paste.app_factory]
      make_app = karl.application:make_app
      [paste.filter_app_factory]
      timeit = karl.timeit:main
      karlerrorpage = karl.errorpage:ErrorPageFilter
      errorlog = karl.errorlog:make_middleware
      [console_scripts]
      addlicense = karl.scripts.addlicense:main
      cssconcat = karl.scripts.cssconcat:main
      evolve = karl.scripts.evolve:main
      generate_stats = karl.scripts.generate_stats:main
      jsconcat = karl.scripts.jsconcat:main
      karl = karl.scripts.karlctl:main
      mvcontent = karl.scripts.mvcontent:main
      samplegen = karl.scripts.samplegen:main
      startover = karl.scripts.startover:main
      """
      )

