' runs test1.html against FF
'saves results as results_fx_Karl_Test_all_suite.html

echo " runs test1.html against FF"
echo "saves results as results_fx_KARL_Test_all_suite.html"

java -jar "selenium-server-1.0.1\selenium-server.jar" -htmlSuite "*firefox" "http://192.168.1.8:6543/" "../all_suite.html" "../log/results_fx_KARL_Test_all_suite.html"

