module.exports = function testWikiEdit (browser, lbParam, verificationErrors)  {

    if (!lbParam) lbParam = {vuSn: 1};
    var assert = require('assert');
    var baseUrl = "http://change-this-to-the-site-you-are-testing/";
    var acceptNextAlert = true;
    browser.get(addUrl(baseUrl, "/communities/selenium_test/"));
    browser.elementByLinkText("WIKI").click();
    browser.elementByLinkText("Edit").click();
    /* ERROR: Caught exception [Error: locator strategy either id or name must be specified explicitly.] */
    browser.elementByXPath("//body[@id='tinymce']").clear();
    browser.elementByXPath("//body[@id='tinymce']").sendKeys("This is the front page. This page is edited by ((selenium))");
    /* ERROR: Caught exception [Error: locator strategy either id or name must be specified explicitly.] */
    /* Warning: assertTextPresent may require manual changes */
    assert.strictEqual(browser.elementByCssSelector("BODY").text().match("^[\\s\\S]*Wiki Page edited[\\s\\S]*$"), true, 'Assertion error: Expected: true, Actual:' browser.elementByCssSelector("BODY").text().match("^[\\s\\S]*Wiki Page edited[\\s\\S]*$"));
    browser.elementByLinkText("OVERVIEW").click();
    browser.elementByLinkText("Second Page").click();
    /* tr> */
    /* 	<td>clickAndWait</td> */
    /* 	<td>link=+</td> */
    /* 	<td></td> */
    /* </tr> */
    /* <tr> */
    /* 	<td>type</td> */
    /* 	<td>//div[@id='save-tags--field']/div/fieldset/div/ul/li/span/input</td> */
    /* 	<td>Third Page</td> */
    /* </tr> */
    /* <tr> */
    /* 	<td>click</td> */
    /* 	<td>save-sendalert</td> */
    /* 	<td></td> */
    /* </tr> */
    /* <tr> */
    /* 	<td>clickAndWait</td> */
    /* 	<td>submit</td> */
    /* 	<td></td> */
    /* </tr> */
    /* <tr> */
    /* 	<td>assertTextPresent</td> */
    /* 	<td>Wiki Page created</td> */
    /* 	<td></td> */
    /* </tr */

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