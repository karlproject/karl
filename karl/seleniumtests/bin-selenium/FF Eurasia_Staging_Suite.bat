' runs test1.html against FF
'saves results as results_fx_staging_eurasia_Suite.html

echo " runs test1.html against FF"
echo "saves results as results_fx_staging_eurasia_Suite.html"

java -jar "selenium-server-1.0.1\selenium-server.jar" -htmlSuite "*firefox" "http://staging.eurasia.sixfeetup.com/" "../staging_Suite.html" "../log/results_fx_staging_eurasia_Suite.html"

