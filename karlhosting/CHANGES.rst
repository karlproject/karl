=======
Changes
=======

- Just recommend using basketweaver

- Add setuptools to the index, so zc.buildout 2.4 bootstrapping gets a
  compatible version

- Fix the naming for ZODB3 and formish to adopt setuptools "local
  identifiers". Otherwise, upgrading to latest setuptools, breaks this

- Change makeindex to, from now, only generate karl4

- Start a karl4 directory and package

- Delete pyramid/staging

- Delete ``prune_index.py``

- Start a README

- Remove the autopull

TODO
====

- Compare the eggs in production buildout to the eggs coming from this,
  need the same version numbers
