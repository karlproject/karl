' runs test1.html against FF
'saves results as results_fx_OSI_all_suite.html

echo " runs test1.html against FF"
echo "saves results as results_fx_OSI_all_suite.html"

java -jar "selenium-server-1.0.1\selenium-server.jar" -htmlSuite "*firefox" "https://karl.soros.org/" "../OSI_suite.html" "../log/results_fx_OSI_Suite.html"

