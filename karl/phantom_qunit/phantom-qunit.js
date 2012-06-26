/**
 * Wait until the test condition is true or a timeout occurs. Useful for waiting
 * on a server response or for a ui change (fadeIn, etc.) to occur.
 *
 * @param testFx javascript condition that evaluates to a boolean,
 * it can be passed in as a string (e.g.: "1 == 1" or "$('#bar').is(':visible')" or
 * as a callback function.
 * @param onReady what to do when testFx condition is fulfilled,
 * it can be passed in as a string (e.g.: "1 == 1" or "$('#bar').is(':visible')" or
 * as a callback function.
 * @param timeOutMillis the max amount of time to wait. If not specified, 3 sec is used.
 */
function waitFor(testFx, onReady, timeOutMillis, timeoutlog) {
    var maxtimeOutMillis = timeOutMillis ? timeOutMillis : 3001, //< Default Max Timout is 3s
        start = new Date().getTime(),
        condition = false,
        interval = setInterval(function() {
            if ( (new Date().getTime() - start < maxtimeOutMillis) && !condition ) {
                // If not time-out yet and condition not yet fulfilled
                condition = (typeof(testFx) === "string" ? eval(testFx) : testFx()); //< defensive code
            } else {
                if(!condition) {
                    // If condition still not fulfilled (timeout but condition is 'false')
                    console.log(timeoutlog || "'waitFor()' timeout");
                    phantom.exit(1);
                } else {
                    // Condition fulfilled (timeout and/or condition is 'true')
                    ///console.log("'waitFor()' finished in " + (new Date().getTime() - start) + "ms.");
                    typeof(onReady) === "string" ? eval(onReady) : onReady(); //< Do what it's supposed to do once the condition is fulfilled
                    clearInterval(interval); //< Stop this interval
                }
            }
        }, 100); //< repeat check every 250ms
}

// parse parameters
var verbose = false;
var xml = false;
var url;
var args = [];
var i = 0;
for (i = 0; i < phantom.args.length; i++) {
    var arg = phantom.args[i];
    if (arg == '-v') {
        verbose = true;
    } else if (arg == '--xml') {
        xml = true;
    } else {
        args.push(arg);
    }
}

if (args.length != 1) {
    console.log('Usage: phantomjs phantom-qunit.js [-v] [--xml] URL');
    phantom.exit();
}
url = args[0]; 

var page = new WebPage();

// Route "console.log()" calls from within the Page context to the main Phantom context (i.e. current "this")
var consoleCatch = '';
function getConsole () {
    var result = consoleCatch;
    consoleCatch = '';
    return result;
}
if (xml) {
    page.onConsoleMessage = function(msg) {
        consoleCatch += msg + '\n';
    };
} else if (verbose) {
    page.onConsoleMessage = function(msg) {
        console.log(msg);
    };
}


function displayNum(num) {
    return ("  " + num).slice(-3);
}

function testResultsVisual () {
    var results = page.evaluate(function(){
        var el = document.getElementById('qunit-testresult');
        console.log(el.innerText + '/n');
        try {
            return {
                total: parseInt(el.getElementsByClassName('total')[0].innerHTML, 10),
                passed: parseInt(el.getElementsByClassName('passed')[0].innerHTML, 10),
                failed: parseInt(el.getElementsByClassName('failed')[0].innerHTML, 10)
            };
        } catch (e) { }
        return {failed: 11111, total: 0, passed: 0};
    });
    var prolog;
    if (results.failed > 0) {
        prolog = '\x1b[31mFAILED\x1b[37m  ';
    } else {
        prolog = '\x1b[32mSUCCESS\x1b[37m ';
    }
    console.log(prolog + 'Total: ' + displayNum(results.total) + 
        ' Failed: ' + displayNum(results.failed) +
        '    ' + url);
    phantom.exit((results.failed > 0) ? 1 : 0);
}


/*
 * <testsuite errors="0" failures="0" name="net.cars.documents.AssuranceTest" tests="1" time="0.207" timestamp="2007-11-02T23:13:49">
 *     <testcase classname="net.cars.documents.AssuranceTest" name="covered" status="passed/failed" >
 *        <failure type="failed" message="..."></failure>
 *     <testcase>
 *     <system-out><![CDATA[]]></system-out>
 *     <system-err><![CDATA[]]></system-err>
 * </testsuite>
 *
 */
function testResultsXml () {
    var results = page.evaluate(function(){
        var el = document.getElementById('qunit-testresult');
        var elModule = document.getElementById('qunit-header');
        var elTests = document.getElementById('qunit-tests');
        var timestamp = new Date().toISOString();
        var url = document.location.href.replace(/\./, '-');
        var cases = [];
        try {
            var moduleTitle = elModule.firstChild.text;
            moduleTitle = moduleTitle.replace(/^ */, '').replace(/ *$/, '')
                .replace(/\./, '-');
            var first = elTests.firstChild;
            while (first) {
                var elDetails = first.getElementsByClassName('fail');
                var j = 0;
                var details = [];
                for (j = 0; j < elDetails.length; j++) {
                    var elDetail = elDetails[j];
                    details.push({
                        type: 'fail',
                        message: elDetail.innerHTML
                    });
                }
                cases.push({
                    name: first.getElementsByClassName('test-name')[0].innerHTML,
                    module: first.getElementsByClassName('module-name')[0].innerHTML.replace(/\./, '-'),
                    status: first.className,
                    details: details
                });
                first = first.nextSibling;
            }
            
            return {
                error: 0,
                total: parseInt(el.getElementsByClassName('total')[0].innerHTML, 10),
                passed: parseInt(el.getElementsByClassName('passed')[0].innerHTML, 10),
                failed: parseInt(el.getElementsByClassName('failed')[0].innerHTML, 10),
                cases: cases,
                log: el.innerText,
                moduleTitle: moduleTitle,
                timestamp: timestamp,
                url: url
            };
        } catch (e) { }
        return {failed: 0, error: 11111, total: 0, passed: 0, cases: [], log: '', moduleTitle: '',
                timestamp: timestamp, url: url};
    });
    console.log('<testsuite errors="' + results.error +
                '" failures="' + results.failed +
                '" name="' + results.url +
                '" tests="' + results.total +
                //'" time="0.207' +
                '" timestamp="'+ results.timestamp +
                '">');
    var i = 0;
    for (i = 0; i < results.cases.length; i++) {
        var testCase = results.cases[i];
        console.log('<testcase classname="' + results.url + '.' + testCase.module +
                    '" name="' + testCase.name +
                    '" status="' + testCase.status +
                    '" >');
        var j = 0;
        for (j = 0; i < testCase.details.length; i++) {
            var detail = testCase.details[j];
            console.log('<failure type="' + detail.type +
                        '" message="' + detail.message +
                        '" />');
        }
        console.log('</testcase>');
    }
    console.log('<system-out><![CDATA[' + getConsole() + '\n' +
                results.log + ']]></system-out>');
    console.log('</testsuite>');
    phantom.exit(0);
}


testResults = xml ? testResultsXml : testResultsVisual;

page.open(url, function(status){
    if (status !== "success") {
        console.log("Unable to access some files. (" + url + ')');
        phantom.exit();
    } else {
        var prolog = '\x1b[31mFAILED\x1b[37m  ';
        var timeoutlog = prolog + 'TIMEOUT                   ' + url;
        waitFor(function(){
            return page.evaluate(function(){
                var el = document.getElementById('qunit-testresult');
                if (el && el.innerText.match('completed')) {
                    return true;
                }
                return false;
            });
        }, testResults, 3001, timeoutlog);
    }
});

