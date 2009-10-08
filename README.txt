Building KARL
=============

Prequisites
-----------

- Your own build of Python 2.5.x (or experimentally, Python 2.6.x).
  This Python should include *both* the SSL and SQLite extensions.
  This means, thus, that OpenSSL and SQLite must be installed.

- Command-line binaries for converting PDF, Word, etc.  These include:
  ppthtml, wvWare, pdftotext, ps2ascii, rtf2xml, xls2csv.  Note that
  these binaries must be on the PATH of the user running the KARL
  application server.

- Install the required system libraries (see below).

Required Libraries
------------------

Karl uses the Python Imaging Library, which requires certain system
libraries. Install the development headers for libjpeg and zlib
(required for accepting JPEG and PNG image uploads, respectively). The
command for installing these libraries varies by operating system. On
Ubuntu, use::

    sudo apt-get install libjpeg-dev zlib1g-dev

On CentOS 5, use::

    sudo yum install libjpeg-devel zlib-devel

On Mac OS X, there are apparently various methods of installing
libraries. Try these or some variation:

    port install gd2
    fink install libjpeg

A web search for "pil os x" provides helpful hints. Note that you do
not need to install PIL itself, only the system libraries that PIL
needs. Also note that if you build PIL without the required libraries,
the build will succeed, but certain Karl tests will probably fail. To
rebuild PIL with new libraries, delete ``eggs/PIL*`` and re-run
``bin/buildout``.

Building
--------

On most Mac OS X or Linux systems with compilation tools and Python
2.5 (2.6 supported, with warnings) installed, you can build the
environment using the following steps:

Check out the buildout from Subversion (replace PROJECT with the project
name)::

  svn co svn+ssh://PROJECT@agendaless.com/home/PROJECT/svn/karl3-PROJECT/trunk karl3

``cd`` into the newly checked out ``karl3`` directory::

  cd karl3

Create a ``virtualenv`` using your existing Python within the
``karl3`` directory (obtain the ``virtualenv`` from `PyPI
<http://pypi.python.org/pypi/virtualenv>`_)::

  virtualenv --no-site-packages .

Bootstrap the installation::

  bin/python bootstrap.py

Run the buildout and wait several minutes for it to finish::

  bin/buildout

You will know the buildout finished successfully when it prints the
following::

   Generated script '/Users/chrism/projects/karl3/bin/twill-sh'.
   Generated script '/Users/chrism/projects/karl3/bin/flunc'.
   buildout: Generated interpreter '/Users/chrism/projects/karl3/bin/python-flunc'.

The buildout process creates a symlink named ``etc`` that initially points
to the ``etc-develop`` directory. If you are building for production
rather than development, redirect the link.  For example::

    ln -sfn etc-deploy etc

Debugging Build Problems
------------------------

Buildout ``default.cfg`` File in Home ``.buildout`` Directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Make sure you don't have a ~/.buildout/default.cfg file; particularly
one that specifies a "download cache".  If you have one of these, the
wrong eggs may be used during installation and the system won't
install cleanly.  An example of such a symptom::

  Error: There is a version conflict.
  We already have: elementtree 1.2.7-20070827-preview
  but repoze.profile 0.6 requires 'elementtree>=1.2.6,<1.2.7'.
  but supervisor 3.0a6 requires 'elementtree>=1.2.6,<1.2.7'.

If you get an error like this or if you have other ``default.cfg``
related problems, either change the ``~/.buildout/default.cfg`` to
disuse a download cache or move the default.cfg aside temporarily,
then delete the ``karl3`` checkout and start over completely.

Starting
--------

After the build finishes successfully, start the system using
supervisord::

  bin/supervisord

Check if it's come up successfully by using ``supervisorctl``::

  bin/supervisorctl status

If it's up successfully, you should see something like the following
as output from ``supervisorctl``::

   karl                             RUNNING    pid 41565, uptime 0:00:45
   zeo                              RUNNING    pid 41486, uptime 0:02:07

Debugging Startup Problems
--------------------------

``ImportError: Failure linking new module`` at startup (lxml)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This has only been witnessed on Mac OS X.  It usually means that the
build found some existing ``libxml2`` or ``libxslt`` instead of the
one that's compiled by the buildout.  It's unclear how this happens,
but it can be resolved by manually setting the MacOS
``DYLD_LIBRARY_PATH``.  For example, if your cwd is the ``karl3``
directory::

  export DYLD_LIBRARY_PATH=`pwd`/parts/libxml2/lib:`pwd`/parts/libxlst/lib:$DYLD_LIBRARY_PATH

Then restart the servers.

Blob layout related startup issue
---------------------------------

If you see an error like this::

  ValueError: Directory layout `zeocache` selected for blob directory /blob dir,
  but marker found for layout `lawn`

It means you've somehow gotten ZODB 3.9 installed instead of the
required ZODB 3.8.  See the resolution steps above in ``Buildout
default.cfg File in Home .buildout Directory`` above to resolve.

Running The Software
--------------------

To use the software, visit `http://localhost:8000/
<http://localhost:8000>`_ in a browser. (Some customizations of KARL
use `http://localhost:6543/ <http://localhost:6543>`_ instead.) When
you see the login page, log in via username: ``admin``, password:
``admin``. After logging in, you should see the "Communities" page.

Debugging Runtime Failures
--------------------------

The application is up but it won't respond to any HTTP requests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Make sure that the ZEO server is started, and that it's listening on
the right port.

Running the Server Without Supervisord
--------------------------------------

To run the "front-end" (the main application), do::

  bin/paster serve etc/karl.ini

To run the "back end" (the ZEO server), do::

  bin/runzeo -C etc/zeo.conf

Keeping Up-To-Date
------------------

If time passes and you'd like to see the changes that have been made
by other developers, you can update your "sandbox" using the
"buildout" command.  From within the ``karl3`` directory::

  svn up
  bin/buildout

The necessary changes will be downloaded.  Then start the servers by
running::

 bin/supervisord

.. or if they're already running::

 bin/supervisorctl reload

In some cases after an update, it may be necessary to run the
``start_over`` script to clear out existing data. If your
sandbox doesn't work properly after updating, run this step to clear
out all existing data (while the ZEO server is running)::

 bin/start_over --yes

Writable checkouts with ``switch``
-----------------------------------

Because we provide anonymous checkouts by default with the buildout,
your ``src`` directory doesn't use a writable svn+ssh by default.
Thus, each time you run buildout, you will need to reset the svn URL
on each directory in ``src``.

A small script is provided at the root of the checkout to make this
easier::

  $ cd src/karl
  $ ../../switch
  $ cd ../karl.content
  $ ../../switch

Do this for any ``src`` directories that you need to make
writeable. Later, when we have released packages that evaluators can
use anonymously, we will get rid of this extra step.

Known Issues
------------

Slowness In Firefox With Firebug and Web Developer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Page load times in KARL3 under Firefox appear slow when either Firebug
and/or the Firefox Web Developer toolkit is installed and enabled.
Disable these tools as necessary or use a different browser to see the
actual system speed.

