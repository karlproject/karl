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

__version__ = '3.96'
import os

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages
from sys import version


here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.txt')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = ''
    CHANGES = ''

requires = [
    'appendonly',
    'Chameleon>=2.0',
    'feedparser',
    'icalendar',
    'lxml',
    'markdown2',
    'perfmetrics',
    'pyramid_multiauth',
    'python-dateutil',
    'Pillow',
    'pyramid',
    'pyramid_zcml',
    'pyramid_formish',
    'pyramid_bottlecap',
    'formish<0.9',
    'repoze.browserid',
    'repoze.catalog',
    'repoze.evolution',
    'repoze.folder',
    'repoze.lemonade',
    'repoze.monty',
    'repoze.postoffice',
    'repoze.sendmail',
    'repoze.session',
    'repoze.who',
    'repoze.whoplugins.zodb',
    'repoze.workflow',
    'setuptools',
    'simplejson',
    'ZODB3',
    # Not really a code depdencency, but used by most buildouts
    # XXX Move to eggs in buildout?
    'repoze.errorlog',
    'supervisor',
]

tests_require = ['coverage', 'mock', 'nose', 'zope.testing']
if version < '2.7':
    tests_require.append('unittest2')

extras_require = {
    'tests': tests_require,
    'kerberos' : ['kerberos']
}


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
      keywords='web wsgi pyramid zope',
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['karl'],
      zip_safe=False,
      install_requires=requires,
      tests_require=tests_require,
      extras_require=extras_require,
      test_suite="karl",
      entry_points = """\
      [paste.app_factory]
      make_app = karl.application:make_app

      [paste.filter_app_factory]
      timeit = karl.timeit:main

      [console_scripts]
      addlicense = karl.scripts.addlicense:main
      evolve = karl.scripts.evolve:main
      generate_stats = karl.scripts.generate_stats:main
      karl = karl.scripts.karlctl:main
      mvcontent = karl.scripts.mvcontent:main
      samplegen = karl.scripts.samplegen:main
      startover = karl.scripts.startover:main
      echo_log = karl.scripts.echo_log:main
      mailout = karl.scripts.mailout:main
      rename_user = karl.scripts.rename_user:main
      reset_security_workflows = karl.scripts.reset_security_workflows:main
      use_pgtextindex = karl.scripts.use_pgtextindex:main
      site_announce = karl.scripts.site_announce:main
      user_activity_report = karl.scripts.user_activity_report:main
      analyze_queries = karl.scripts.analyze_queries:main
      juice_all = karl.scripts.juice_all:main
      test_phantom_qunit = karl.scripts.test_phantom_qunit:main

      [karlserve.scripts]
      generate_stats = karl.scripts.generate_stats:config_parser
      init_repozitory = karl.scripts.init_repozitory:config_parser
      """
      )
