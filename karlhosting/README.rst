=================================
Generating the KARL Package Index
=================================

Usage
=====

- Put your packages in ``karl4``

- ``python makeindex.py``

- Commit the changes and push

- During deployment, each app server will do a ``git pull`` as its
  first step, getting an updated copy of the index

Package Indexes
===============

In July 2015 we started a new index at ``/karl4``. We left the
``pyramid`` directory and index in place for historical reasons,
although it is no longer being scanned and updated by the
``makeindex`` script.


