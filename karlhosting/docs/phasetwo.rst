==================================
Phase Two - OSF Current Production
==================================

There is a discussion about migrating OSF's production instance from
its current hosting arrangement to a new one at gocept.

While this step isn't a dramatic difference machine-wise from the
Phase One step, it does imply some delegation of services as discussed
later.

Open Questions
==============

- In what country?  Presumably Germany, as it might be prohibitively
  expensive or disruptive for gocept to get their operations going in
  the U.S.

- What is the system used for monitoring?  (I propose a for-fee web
  service but OSF might have an internal system.)

- Can we say we are conforming to German privacy standards?

Production App Server
=====================

- 2 GB RAM
- 100 GB disk
- Invoiced to Agendaless

At this point we will have 2 app server VMs, one for staging and one
for production.  Robert and OSF will be responsible for any offsite
backups.

Robert/Chris/Tres can all easily do production updates using Chris's
new approach.  Stated differently, gocept will not need to do KARL
application updates in this phase.

In the transition to Phase Two, we will complete the switch to github
and packages.  At that point, OSF will no longer have a vendor
(Agendaless) in charge of the source code repository.  Agendaless is
currently paying for the private Github account but that can be
transfered whenever appropriate.

Production DB Server
====================

- 2 GB RAM
- 200 GB disk
- Invoiced to Agendaless

In this phase, gocept formally becomes the "owner" of the DB Server.
The app server team treats it as a black box and has no shell login.

gocept provides this DB Service as a flat fee for the VM plus services
on a not-to-exceed hourly basis for:

- Monitoring. They notice if the host is having CPU/memory/disk issues
  and corrects the issue.  They also notice if PostgreSQL is having an
  issue and correct it.

- Backup/restore.  Ensure that a basic level of PostgreSQL (data and
  configuration) backup is being done.

- Dry run.  Before going live, we "accidentally" wipe out the
  production instance and see if we can restore from backup.

- Tuning.  Make sure PostgreSQL's out-of-the-box tuning is modified to
  match our profile.

- Near-line snapshots (last 3 dailies, last 2 weeklies, 1 month ago, 6
  months ago, 1 year ago)

- Restore from a near-line snapshot.

Questions
---------

- Is putting the DB Server in a VM a bad idea?  (5% performance hit,
  only one core)

Mail Server
===========

KARL has an email-in and email-out capability.  This service needs to
run somewhere and somebody needs to "own" it.

- Incoming mail

- Outgoing mail

- Basic spam and vacation support

- Backup/restore, monitoring, logfile rotation, etc.

Production Services
===================

We need to discuss the following and see which are done by gocept
versus being done by the development team.

- Monitoring

- OS upgrades

- Appserver Backups

- GSA sync

- Log file analysis

Question
--------

- If we needed to "promote" staging to production due to VM failure,
  can gocept do something IP-wise here?

Application Support
===================

For KARL itself, gocept will receive no support requests from OSF.

- What is the system we (OSF, Agendaless) will use for bug reports?

- Handling the karldemo site

- nginx/uwsgi
