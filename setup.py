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

__version__ = '4.31.1'
import os

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
    'admin5',
    'appendonly',
    'Chameleon>=2.0',
    'feedparser',
    'icalendar',
    'j1m.relstoragejsonsearch >=0.2.2',
    'lxml',
    'markdown2',
    'perfmetrics>=2.0',
    'pyramid_multiauth',
    'pyramid_jwtauth',
    'pyramid_zodbconn',
    'python-dateutil',
    'python-slugify',
    'Pillow',
    'pyramid',
    'pyramid_formish',
    'pyramid_tm',
    'pyramid_zcml',
    'formish<0.9',
    'redis', # archive to box
    'repoze.browserid',
    'repoze.catalog>=0.8.3',  # 'total' attribute of numdocs
    'repoze.depinj',
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
    'requests',  # used by box client code
    'requests_toolbelt',
    'zope.interface',
    'wsgicors', # jwtauth
    'user-agents',
    'pysaml2',
    'pyyaml',
]

tests_require = ['coverage', 'mock', 'nose', 'zope.testing']
if version < '2.7':
    requires.append('argparse')
    tests_require.append('unittest2')

extras_require = {
    'tests': tests_require,
    'performance': ['slowlog'],
    'redislog': ['redis']
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
      main = karl.application:main

      [paste.filter_app_factory]
      timeit = karl.timeit:main

      [console_scripts]
      addlicense = karl.scripts.addlicense:main
      backdate = karl.scripts.backdate:main
      chown = karl.scripts.chown:main
      evolve = karl.scripts.evolve:main
      generate_stats = karl.scripts.generate_stats:main
      karl = karl.scripts.karlctl:main
      karlctl = karl.scripts.karlctl:main
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
      test_phantom_qunit = karl.scripts.test_phantom_qunit:main
      init_repozitory = karl.scripts.init_repozitory:main
      clean_tags = karl.scripts.cleantags:main
      usersync = karl.scripts.usersync:main
      remove_extracted_data = karl.scripts.remove_extracted_data:main
      create_mailin_trace = karl.scripts.create_mailin_trace:main
      debug = karl.scripts.debug:main
      digest = karl.scripts.digest:main
      add_feed = karl.scripts.feeds:add_feed
      edit_feed = karl.scripts.feeds:edit_feed
      remove_feed = karl.scripts.feeds:remove_feed
      update_feeds = karl.scripts.feeds:update_feeds
      list_feeds = karl.scripts.feeds:list_feeds
      mailin = karl.scripts.mailin:main
      load_peopleconf = karl.scripts.peopleconf:load
      dump_peopleconf = karl.scripts.peopleconf:dump
      reindex_text = karl.scripts.reindex_text:main
      reindex_catalog = karl.scripts.reindex_catalog:main
      adduser = karl.scripts.adduser:main
      reindex_peopledir = karl.scripts.reindex_peopledir:main
      archive = karl.box.archive:archive_console
      arc2box = karl.box.archive:worker
      reset_passwords = karl.scripts.reset_passwords:main
      remove_forum_acls = karl.scripts.remove_forum_acls:main
      set_password_expiration = karl.scripts.set_password_expiration:main
      password_reset_reminder = karl.scripts.password_reset_reminder:main
      json_updater = karl.scripts.json_updater:main
      pgevolve = karl.scripts.pgevolve:main
      """
      )
