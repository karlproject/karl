' runs test1.html against IE
'saves results as results_ie_Ariadne_production_Suite.html

echo " runs test1.html against IE"
echo "saves results as results_ie_Ariadne_production_Suite.html"

java -jar "selenium-server-1.0.1\selenium-server.jar" -htmlSuite "*iexplore" "https://portal.ariadne-network.eu" "../production_suite.html" "../log/results_ie_Ariadne_production_Suite.html"

