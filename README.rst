=============================
Get Started Quickly With Karl
=============================

PostgreSQL
----------

Karl requires PostgreSQL be installed on your system. 9.4 or higher is required.

Relstorage
----------

Create the user and database for the PostgreSQL/Relstorge based instance of
Karl::

  $ createuser -P karltest
    (Enter 'test' for password.  Repeat.  Answer 'n' to next three questions.)
  $ createdb -O karltest karltest

Later, if you want to blow away the database and start over::

  $ dropdb karltest; createdb -O karltest karltest

Run the updater, bin/json_updater and keep it running as long as
you're making database changes.

Buildout
--------
Check out the buildout from github::

  $ git clone git@github.com:karlproject/karl.git
  $ cd karl

Create a virtual environment and run the buildout::

  $ virtualenv -p python2.7 .
  $ bin/python bootstrap-buildout.py
  $ bin/buildout

Karl is now built and ready to run. To start Karl and some support processes::

  $ bin/supervisord

You can see what's running with::

  $ bin/supervisorctl status

At least the karl and updater processes should be running.

You'll need to apply some Postgres schema updates with::

  $ bin/pgevolve -l

Visit the test instance of Karl at::

  http://localhost:6543/

Default login and password are admin/admin.

To shutdown all of the processes, use::

  $ bin/supervisorctl shutdown

Localization of date formats
----------------------------

Karl uses the Globalize javascript library to handle date formatting. It is
recommended that whenever you need to use a date in a Karl or customization
package template, you use Karl's globalize mechanism instead of formatting
the date in Python code.

To use gloablize, it's best to serve the date to the template in one of two
formats: 'dd/mm/yyyy' for dates and 'dd/mm/yyyy hh:mm:ss' for dates with
times. In the template, the date has to be by itself inside a tag and must
use one of the globalize classes:

  - globalize-short-date:
    MM/dd/yyyy (02/15/2012)
  - globalize-long-date:
    MMMM dd yyyy (February 15 2012)
  - globalize-full-date:
    dddd, MMMM dd yyyy HH:mm (Wednesday, February 15 2012 12:00)
  - globalize-date-time:
    M/d/yyyy HH:mm (2/15/2012 12:00)
  - globalize-calendar-full:
    dddd M/d (Wednesday 2/15)
  - globalize-calendar-abbr:
    ddd M/d (Wed 2/15)
  - globalize-calendar-long:
    dddd, MMMM d (Wednesday, February 15)
  - globalize-calendar-list:
    ddd, MMM d (Wed, Feb 15)

Globalize will convert the date to the proper format for the current
culture on page load. Default culture is en-US.

As an example::

  <h3 class="globalize-long-date">02/15/2012</h3>

Will display an h3 title with the date 'February 15 2012'. The same date will
show up as '15 February 2012' if the user has 'europe' as date format default.

Hacking
-------

To hack on some source code::

  $ bin/develop co osi
  $ bin/buildout -No

Source code will now be in src/osi.

When playing with the code it's usually very useful to have some sample
content added to the site, so that it looks a bit closer to a real site.
The karlserve command can be used for that::

  $ bin/karlserve samplegen

Using this command 10 sample communities will be added to the site, each
with their own wikis, blogs, calendars and files.

The samplegen command does not create intranets, so they need to be added
manually if they are required. To do that visit your instance at:

  http://localhost:6543/pg/add_community.html

Fill the form to add a community, making sure the 'intranets' checkbox is
selected. An 'intranets' tab will be visible on the community pages after
that, from which new intranets can be added.

If you need to work with versioning, you need to initialize the repository
before the versioning UI will show up. This is done with::

  $ bin/karlserve init_repozitory pg

If you are working on frontend static assets (JS, CSS) then you need to
re-build the "compiled" JS and CSS:

- cd src/karl

- npm install

- node_modules/.bin/gulp install

Enjoy!

