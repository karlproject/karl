===================
Phase One - Staging
===================

We have an immediate need for a staging environment for OSF's
KARL. The functions include:

- Testing bug fixes including distribution lists, phase 1

- Testing the implementation of distribution lists, phase 2

- LiveSearch final evaluation and final testing

- OSF evaluation of the new search architecture

- Files mockup for Upload Multiple

In this step we will deploy a cluster of services and the technical
support needed for it.

Staging App Server
==================

- 2 GB RAM
- 100 GB disk
- Invoiced to Agendaless

We will use this app server box for the following functionality:

- Testing the current codebase with a KARL appserver and ZEO server
  running a snapshot of data from the production KARL.  This will be
  for testing distribution lists and bug fixes.

- The app server side of new search architecture.

- Incoming and outgoing mail in Phase One, unless gocept can agree to
  run a Postfix for us.

We will use this as the opportunity to upgrade many of our core
packages: switch to Python 2.6.x, newer ZODB, etc.

Robert, Chris Rossi, Tres, and Paul will have SSH logins.  In this
phase they will perform 100% of the support for the functionality
listed above:

- Monitoring.

- Upgrades.

- Restarts.

- Debugging.

- Connecting to GSA sync.

- Any appropriate backups.

- Ensuring services survive reboot.

In this phase, there will be none of the following:

- Failover of any kind.

- Distribution of requests to more than one CPU core.

- Log file analysis.

Additionally, we will collect whatever factors influence the go/no-go
decision on production deployment in Germany.  We'll then make any
measurements and have a final go/no-go decision.

Questions
---------

- What is the process and turnaround time for getting more VMs?

- What is the KVM process of increasing RAM?  Disk?

- Do we have the expertise on Postfix?


Staging DB Server
=================

- 2 GB RAM
- 200 GB disk
- Invoiced to Agendaless

- Multiple staging databases

- RelStorage and pgtextindex

- "Owned" by gocept with bundled support (minimal in this step)

- Tuning is done at the hourly rate
