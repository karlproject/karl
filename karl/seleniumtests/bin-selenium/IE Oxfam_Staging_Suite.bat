' runs test1.html against IE
'saves results as results_ie_karlhost01_OXFAM_Suite.html

echo " runs test1.html against IE"
echo "saves results as results_ie_karlhost01_OXFAM_Suite.html"

java -jar "selenium-server-1.0.1\selenium-server.jar" -htmlSuite "*iexplore" "http://karlhost01.sixfeetup.com:8500/" "../all_suite1.html" "../log/results_ie_karlhost01_OXFAM_Suite.html"

