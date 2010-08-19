' runs test1.html against IE
'saves results as results-IE.html

echo " runs test1.html against IE"
echo "saves results as results-IE.html"

java -jar "..\selenium-server-1.0.1\selenium-server.jar" -htmlSuite "*iexplore"   "http://garish:81/" "..\test1.html" "..\results2-ie.html"
