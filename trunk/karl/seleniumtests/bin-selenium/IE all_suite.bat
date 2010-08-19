' runs test1.html against IE
'saves results as results_ie_KARL_Test_all_suite.html

echo " runs test1.html against IE"
echo "saves results as results_ie_Karl_Test_all_suite.html"

java -jar "selenium-server-1.0.1\selenium-server.jar" -htmlSuite "*iexplore" "http://192.168.1.8:6543/" "../all_suite.html" "../log/results_ie_KARL_Test_all_suite.html"

