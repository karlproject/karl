' runs test1.html against IE
'saves results as results_ie_staging-fahamu_suite.html

echo " runs test1.html against IE"
echo "saves results as results_ie_staging_fahamu_suite.html"

java -jar "selenium-server-1.0.1\selenium-server.jar" -htmlSuite "*iexplore" "http://staging.fahamu.sixfeetup.com/" "../all_suite.html" "../log/results_ie_staging_fahamu_suite.html"

