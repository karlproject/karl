Introduction



This is documentation for end user testing utilizing selenium as a tool for Karl web  sites.
The individual tests can be run or the suite which will run series of tests against entire web instance.
There are .bat files for testing under IE7  or Firefox and can be set up to target different instances
 such as the localhost:6543, garish:81, garish:8100, garish:8200 or production instances kdi-dev.sixfeetup.com.

How to Run test suite:

The tests consists of running test1.bat utilizing either IE or FF for example:

IEtest1.bat

' runs test1.html against IE
'saves results as results-IE.html

echo " runs test1.html against IE"
echo "saves results as results-IE.html"

java -jar "..\selenium-server-1.0.1\selenium-server.jar" -htmlSuite "*iexplore"   "http://garish:81/" "..\test1.html" "..\results2-ie.html"

or

FFtest1.bat

'runs test1.html against FF
'saves results as results-ff.html

echo " runs test1.html against FF"
echo "saves results as results-ff.html"

java -jar "..\selenium-server-1.0.1\selenium-server.jar" -htmlSuite "*firefox" "http://garish:81/" "..\test1.html" "..\results-ff.html"

for new tests
1. change comments as needed
2. change the server address as needed
3. change the test to run "../all_suite.html"
4. change the result/log file to save "../log/results_fx_garish_" + name of test
   bin/server1
   192.168.2.3
   garish
   osi-karl3

By changing test1.html to all_suite.html for each of the above .bat files and changing the name of the ouput file to identify the 
server (I.e. results-ff.html changes to results-ff-server-all-suite.html where server=garish). 

The following are the tests that run under seleniums test suite named all_suite.html.
The test creates the needed parameters (i.e community) and removes the necessary parameters (i.e community). 
If an error occurs the housekeeping can be achieved by re-running once the problem is fixed.

login_admin 
make_community
community_search 
blog_view
blogentry_add
blog_search
blogentry_edit 
blogentry_delete 
calendar_view 
calendar_add_event 
calendar_search 
calendar_edit_event 
calendar_delete_event 
files_view 
files_search 
files_add_folder 
files_delete_folder 
wiki_view 
wiki_search 
wiki_edit 
forums_view 
forums_search 
forums_add 
forums_edit 
forums_delete 
offices_view 
offices_search 
add_tags 
view_tags 
profiles_manage_tags_edit 
profiles_edit 
profiles_search 
delete_tags 
remove_community 
logout
