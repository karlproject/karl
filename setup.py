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

__version__ = '3.3-dev'

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
    'setuptools',
    'repoze.bfg',
    'repoze.retry',
    'repoze.tm2',
    'repoze.monty',
    'ZODB3',
    'repoze.catalog',
    'repoze.folder',
    'repoze.evolution',
    'repoze.zodbconn',
    'repoze.lemonade',
    'repoze.who',
    'repoze.whoplugins.zodb',
    'repoze.session',
    'repoze.browserid',
    'lxml',
    'nose',
    'FormEncode',
    'simplejson',
    'coverage',
    'repoze.sendmail',
    'repoze.workflow',
    'feedparser',
    'zope.testing', # fwd compat when not directly relied on by BFG
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
      [paste.filter_app_factory]
      timeit = karl.timeit:main
      karlerrorpage = karl.errorpage:ErrorPageFilter
      [console_scripts]
      addlicense = karl.scripts.addlicense:main
      debug = karl.scripts.debug:main
      evolve = karl.scripts.evolve:main
      export_usage_metadata = karl.scripts.export_usage_metadata:main
      jsconcat = karl.scripts.jsconcat:main
      karlctl = karl.scripts.karlctl:main
      mkprivate = karl.scripts.mkprivate:main
      peopleconf = karl.scripts.peopleconf:main
      reindex_catalog = karl.scripts.reindex_catalog:main
      update_feeds = karl.scripts.update_feeds:main
      """
      )

