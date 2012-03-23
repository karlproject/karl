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
function waitFor(testFx, onReady, timeOutMillis) {
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
                    console.log("'waitFor()' timeout");
                    phantom.exit(1);
                } else {
                    // Condition fulfilled (timeout and/or condition is 'true')
                    console.log("'waitFor()' finished in " + (new Date().getTime() - start) + "ms.");
                    typeof(onReady) === "string" ? eval(onReady) : onReady(); //< Do what it's supposed to do once the condition is fulfilled
                    clearInterval(interval); //< Stop this interval
                }
            }
        }, 100); //< repeat check every 250ms
}

// parse parameters
var verbose = false;
var url;
if (phantom.args.length >= 1 && phantom.args.length <= 2) {
    if (phantom.args[0] == '-v' && phantom.args.length == 2) {
        url = phantom.args[1];
        verbose = true;
    } else if (phantom.args[1] == '-v') {
        verbose = true;
        url = phantom.args[0];
    } else if (phantom.args.length == 1) {
        url = phantom.args[0];
    }
}

if (! url) {
    console.log('Usage: phantomjs phantom-qunit.js [-v] URL');
    phantom.exit();
}

var page = new WebPage();

// Route "console.log()" calls from within the Page context to the main Phantom context (i.e. current "this")
if (verbose) {
    page.onConsoleMessage = function(msg) {
        console.log(msg);
    };
}

page.open(url, function(status){
    if (status !== "success") {
        console.log("Unable to access network");
        phantom.exit();
    } else {
        waitFor(function(){
            return page.evaluate(function(){
                var el = document.getElementById('qunit-testresult');
                if (el && el.innerText.match('completed')) {
                    return true;
                }
                return false;
            });
        }, function(){
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
                prolog = '\x1b[31mFAILED\x1b[37m ';
            } else {
                prolog = '\x1b[32mSUCCESS\x1b[37m ';
            }
            console.log(prolog + 'Total: ' + results.total + 
                ', Failed: ' + results.failed +
                '    of ' + phantom.args[0]);
            phantom.exit((results.failed > 0) ? 1 : 0);
        });
    }
});

