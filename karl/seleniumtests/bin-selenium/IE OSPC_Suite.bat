' runs test1.html against IE
'saves results as results_ie_kdi-dev_OSPC_Suite.html

echo " runs test1.html against IE"
echo "saves results as results_ie_kdi-dev_OSPC_all_suite.html"

java -jar "selenium-server-1.0.1\selenium-server.jar" -htmlSuite "*iexplore" "http://kdi-dev.sixfeetup.com:8300/" "../OSPC_Suite.html" "../log/results_ie_kdi-dev_OSPC_Suite.html"

