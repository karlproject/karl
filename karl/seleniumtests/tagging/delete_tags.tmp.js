module.exports = function testDeleteTags (browser, lbParam, verificationErrors)  {

    if (!lbParam) lbParam = {vuSn: 1};
    var assert = require('assert');
    var baseUrl = "http://change-this-to-the-site-you-are-testing/";
    var acceptNextAlert = true;
    browser.get(addUrl(baseUrl, "/communities/selenium_test/view.html"));
    browser.elementByLinkText("My Profile").click();
    browser.elementByLinkText("Manage Tags").click();
    /* Warning: verifyTextPresent may require manual changes */
    try {
        assert.strictEqual(browser.elementByCssSelector("BODY").text().match("^[\\s\\S]*Manage Tags[\\s\\S]*$"), true, 'Assertion error: Expected: true, Actual:' browser.elementByCssSelector("BODY").text().match("^[\\s\\S]*Manage Tags[\\s\\S]*$"));
    } catch (e) {
        verificationErrors && verificationErrors.push(e.toString());
    }
    /* ERROR: Caught exception [Error: locator strategy either id or name must be specified explicitly.] */

};

function isAlertPresent(browser) {
    try {
        browser.alertText();
        return true;
    } catch (e) {
        return false;
    }
}

function closeAlertAndGetItsText(browser, acceptNextAlert) {
    try {
        var alertText = browser.alertText() ;
        if (acceptNextAlert) {
            browser.acceptAlert();
        } else {
            browser.dismissAlert();
        }
        return alertText;
    } catch (ignore) {}
}

function isEmptyArray(arr){
    return !(arr && arr.length);
}

function addUrl(baseUrl, url){
    if (endsWith(baseUrl, url))
        return baseUrl;

    if (endsWith(baseUrl,"/") && startsWith(url,"/"))
        return baseUrl.slice(0,-1) + url;

    return baseUrl + url;
}

function endsWith(str,endStr){
    if (!endStr) return false;

    var lastIndex = str && str.lastIndexOf(endStr);
    if (typeof lastIndex === "undefined") return false;

    return str.length === (lastIndex + endStr.length);
}

function startsWith(str,startStr){
    var firstIndex = str && str.indexOf(startStr);
    if (typeof firstIndex === "undefined")
        return false;
    return firstIndex === 0;
}

function waitFor(browser, checkFunc, timeout, pollFreq){
    var val;
    if (!timeout)
        timeout = 30000;
    if (!pollFreq)
        pollFreq = 200;
    while(!val) {
        val = checkFunc(browser);
        if (val)
            break;
        if (timeout < 0) {
            require("assert").throws("Timeout");
            break;
        }
        browser.sleep(pollFreq);
        timeout -= pollFreq;
    }

    return val;
}