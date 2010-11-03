' runs test1.html against FF
'saves results as results_fx_Ospc_staging_suite.html

echo " runs test1.html against FF"
echo "saves results as results_fx_Ospc_staging_suite.html"

java -jar "selenium-server-1.0.1\selenium-server.jar" -htmlSuite "*firefox" "http://staging.ospc.sixfeetup.com/" "../staging_suite1.html" "../log/results_fx_Ospc_staging_suite.html"

