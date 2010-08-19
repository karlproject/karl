' runs test1.html against FF
'saves results as results_fx_Fahamu_production_Suite.html

echo " runs test1.html against FF"
echo "saves results as results_fx_Fahamu_production_Suite.html"

java -jar "selenium-server-1.0.1\selenium-server.jar" -htmlSuite "*firefox" "https://intranet.fahamu.org/" "../production_suite.html" "../log/results_fx_Fahamu_production_Suite.html"

