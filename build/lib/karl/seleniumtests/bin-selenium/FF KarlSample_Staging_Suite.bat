' runs test1.html against FF
'saves results as results_fx_karlhost01_KarlSample_Suite.html

echo " runs test1.html against FF"
echo "saves results as results_fx_karlhost01_KarlSample_Suite.html"

java -jar "selenium-server-1.0.1\selenium-server.jar" -htmlSuite "*firefox" "http://karlhost01.sixfeetup.com:6543/" "../all_suite.html" "../log/results_fx_karlhost01_KarlSample_Suite.html"

