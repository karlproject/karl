' runs test1.html against IE
'saves results as results_ie_GCFE_staging_Suite.html

echo " runs test1.html against IE"
echo "saves results as results_ie_GCFE_staging_Suite.html"

java -jar "selenium-server-1.0.1\selenium-server.jar" -htmlSuite "*iexplore" "http://staging.gcfe.sixfeetup.com/" "../staging_suite1.html" "../log/results_ie_GCFE_staging_Suite.html"

