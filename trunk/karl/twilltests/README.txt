Twill tests for Karl
==========================

Twill
--------------------------
Twill is a simple language that supports automated web site testing by allowing users to browse a web site from a command-line interface.

Site: http://twill.idyll.org/

Flunc
--------------------------

"Flunc is a simple over-the-web functional testing application that uses twill scripts."
(quoted from flunc's website)

Site: http://www.coactivate.org/projects/flunc/project-home


Tests for Karl website
--------------------------
Twill and Flunc have been installed as part of this installation. 
We have written twill tests that flunc can run to verify this installation and its tool's functionality.  These tests can be run at any time, but have been organized to help developers verify their work does not "damage" other parts of the site. We have organized these tests into directories in order to allow the developer to run twill tests against the whole installation or run tests against just the function/tool that is being worked on. 

to run:
You can run these tests from the twilltests directory by running
flunc testname

or you can use the -p flag to tell flunc where the tests directory is:
flunc -p src/karl/karl/twilltests testname

Here are some other useful flags that you can use for flunc
-i, --interactive-debug   Fall into twill shell on error
-F, --ignore-failures     continue running tests after failures
-C, --cleanup-only        run only the suite cleanup and not the tests
-X, --no-cleanup          do not run cleanup handlers for suites

and more at:
http://www.coactivate.org/projects/flunc/project-home/#debugging


=======================
Running Tests:
=======================
To run the "all" test which runs tests against the major functionality of the site.
All/Everything test:
flunc -p src/karl/karl/twilltests all

Other tests which test only their specific functionality (most are already run as part of all suite)
Blog: 
flunc -p src/karl/karl/twilltests blog

Calendar:
flunc -p src/karl/karl/twilltests calendar

Community:
flunc -p src/karl/karl/twilltests community

Files:
flunc -p src/karl/karl/twilltests files

Forums:
flunc -p src/karl/karl/twilltests forums

Offices: 
flunc -p src/karl/karl/twilltests offices

Profiles:
flunc -p src/karl/karl/twilltests profiles

Search: 
flunc -p src/karl/karl/twilltests search

Tagging:
flunc -p src/karl/karl/twilltests tagging

Wiki:
flunc -p src/karl/karl/twilltests wiki