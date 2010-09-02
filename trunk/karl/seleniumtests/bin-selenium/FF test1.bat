' runs test1.html against FF
'saves results as results-ff.html

echo " runs test1.html against FF"
echo "saves results as results-ff.html"

java -jar "..\selenium-server-1.0.1\selenium-server.jar" -htmlSuite "*firefox" "http://garish:81/" "..\test1.html" "..\results-ff.html"

