' runs test1.html against FF
'saves results as results_fx_Karlhost01_Fahamu_Suite.html

echo " runs test1.html against FF"
echo "saves results as results_fx_Karlhost01_Fahamu_Suite.html"

java -jar "selenium-server-1.0.1\selenium-server.jar" -htmlSuite "*firefox" "http://karlhost01.sixfeetup.com:8200/" "../all_suite.html" "../log/results_fx_Karlhost01_Fahamu_Suite.html"

