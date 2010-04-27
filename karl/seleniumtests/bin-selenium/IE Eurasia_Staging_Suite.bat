' runs test1.html against IE
'saves results as results_ie_karlhost01_Eurasia_Suite.html

echo " runs test1.html against IE"
echo "saves results as results_ie_karlhost01_Eurasia_Suite.html"

java -jar "selenium-server-1.0.1\selenium-server.jar" -htmlSuite "*iexplore" "http://karlhost01.sixfeetup.com:8100/" "../all_suite.html" "../log/results_ie_karlhost01_Eurasia_Suite.html"

