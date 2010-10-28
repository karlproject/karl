' runs test1.html against FF
'saves results as results_fx_Ariadne_production_suite.html

echo " runs test1.html against FF"
echo "saves results as results_Ariadne_production_suite.html"

java -jar "selenium-server-1.0.1\selenium-server.jar" -htmlSuite "*firefox" "https://portal.ariadne-network.eu/" "../production_suite.html" "../log/results_fx_Ariadne_production_suite.html"

