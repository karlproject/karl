module.exports = function testCalendarSuiteTmp (browser, lbParam, verificationErrors)  {

    if (!lbParam) lbParam = {vuSn: 1};
    var assert = require('assert');
    var baseUrl = "http://change-this-to-the-site-you-are-testing/";
    var acceptNextAlert = true;
    browser.get(addUrl(baseUrl, "/login.html"));
    /* ERROR: Caught exception [Error: locator strategy either id or name must be specified explicitly.] */
    /* ERROR: Caught exception [Error: locator strategy either id or name must be specified explicitly.] */
    /* ERROR: Caught exception [Error: locator strategy either id or name must be specified explicitly.] */
    /* Warning: verifyTextPresent may require manual changes */
    try {
        assert.strictEqual(browser.elementByCssSelector("BODY").text().match("^[\\s\\S]*Communities[\\s\\S]*$"), true, 'Assertion error: Expected: true, Actual:' browser.elementByCssSelector("BODY").text().match("^[\\s\\S]*Communities[\\s\\S]*$"));
    } catch (e) {
        verificationErrors && verificationErrors.push(e.toString());
    }
    browser.get(addUrl(baseUrl, "/communities/?titlestartswith=T"));
    browser.elementByXPath("//div[@id='center']/div/div[4]/div[1]/a").click();
    browser.elementByLinkText("CALENDAR").click();
    /* Warning: assertTextPresent may require manual changes */
    assert.strictEqual(browser.elementByCssSelector("BODY").text().match("^[\\s\\S]*Add Event[\\s\\S]*$"), true, 'Assertion error: Expected: true, Actual:' browser.elementByCssSelector("BODY").text().match("^[\\s\\S]*Add Event[\\s\\S]*$"));
    browser.get(addUrl(baseUrl, "/communities/test_selenium/view.html"));
    browser.elementByLinkText("CALENDAR").click();
    browser.elementByLinkText("Add Event").click();
    /* ERROR: Caught exception [Error: locator strategy either id or name must be specified explicitly.] */
    browser.elementByXPath("//fieldset[@id='startdate-field']/span[1]/select[1]").elementByXPath('option[text()="12"][1]').click();
    browser.elementByXPath("//fieldset[@id='startdate-field']/span[1]/select[2]").elementByXPath('option[text()="30"][1]').click();
    browser.elementByXPath("//fieldset[@id='enddate-field']/span/select[2]").elementByXPath('option[text()="45"][1]').click();
    /* ERROR: Caught exception [Error: locator strategy either id or name must be specified explicitly.] */
    /* ERROR: Caught exception [Error: locator strategy either id or name must be specified explicitly.] */
    /* ERROR: Caught exception [Error: locator strategy either id or name must be specified explicitly.] */
    /* ERROR: Caught exception [Error: locator strategy either id or name must be specified explicitly.] */
    /* ERROR: Caught exception [Error: locator strategy either id or name must be specified explicitly.] */
    /* ERROR: Caught exception [Error: locator strategy either id or name must be specified explicitly.] */
    /* Warning: assertTextPresent may require manual changes */
    assert.strictEqual(browser.elementByCssSelector("BODY").text().match("^[\\s\\S]*calendar123[\\s\\S]*$"), true, 'Assertion error: Expected: true, Actual:' browser.elementByCssSelector("BODY").text().match("^[\\s\\S]*calendar123[\\s\\S]*$"));
    /* Warning: assertTextPresent may require manual changes */
    assert.strictEqual(browser.elementByCssSelector("BODY").text().match("^[\\s\\S]*Staff One[\\s\\S]*$"), true, 'Assertion error: Expected: true, Actual:' browser.elementByCssSelector("BODY").text().match("^[\\s\\S]*Staff One[\\s\\S]*$"));
    /* Warning: assertTextPresent may require manual changes */
    assert.strictEqual(browser.elementByCssSelector("BODY").text().match("^[\\s\\S]*karltest@mailinator\\.com[\\s\\S]*$"), true, 'Assertion error: Expected: true, Actual:' browser.elementByCssSelector("BODY").text().match("^[\\s\\S]*karltest@mailinator\\.com[\\s\\S]*$"));
    browser.elementByLinkText("Edit").click();
    /* ERROR: Caught exception [Error: locator strategy either id or name must be specified explicitly.] */
    /* ERROR: Caught exception [Error: locator strategy either id or name must be specified explicitly.] */
    /* Warning: assertTextPresent may require manual changes */
    assert.strictEqual(browser.elementByCssSelector("BODY").text().match("^[\\s\\S]*calendar234[\\s\\S]*$"), true, 'Assertion error: Expected: true, Actual:' browser.elementByCssSelector("BODY").text().match("^[\\s\\S]*calendar234[\\s\\S]*$"));
    /*  Delete calendar event */
    browser.elementByLinkText("Delete").click();
    /* Warning: assertTextPresent may require manual changes */
    assert.strictEqual(browser.elementByCssSelector("BODY").text().match("^[\\s\\S]*Do you really want to delete calendar234 [\\s\\S]\n ok cancel[\\s\\S]*$"), true, 'Assertion error: Expected: true, Actual:' browser.elementByCssSelector("BODY").text().match("^[\\s\\S]*Do you really want to delete calendar234 [\\s\\S]\n ok cancel[\\s\\S]*$"));
    browser.elementByLinkText("ok").click();

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