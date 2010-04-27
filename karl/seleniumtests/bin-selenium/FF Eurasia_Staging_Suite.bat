' runs test1.html against FF
'saves results as results_fx_karlhost01_Eurasia_Suite.html

echo " runs test1.html against FF"
echo "saves results as results_fx_karlhost01_Eurasia_Suite.html"

java -jar "selenium-server-1.0.1\selenium-server.jar" -htmlSuite "*firefox" "http://karlhost01.sixfeetup.com:8100/" "../Eurasia_Suite.html" "../log/results_fx_karlhost01_Eurasia_Suite.html"

