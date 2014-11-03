
/* jshint expr: true, node: true, globalstrict: true */
'use strict';

var chai = require('chai');
var chaiAsPromised = require('chai-as-promised');
chai.use(chaiAsPromised);
var expect = chai.expect;
var _ = require('lodash');
var protractor = require('protractor');
var by = protractor.By;
var URL = require('url');

function resolve(path) {
  var browser = global.browser;
  // make sure path is added _relative_ to the site
  return browser.baseUrl + path;
}

function loginAsAdmin() {
  // this logs in only if needed, so it can be
  // safely used as beforeEach.
  var browser = global.browser;
  return browser.getCurrentUrl().then(function(url) {
    var needsToLoad = url.indexOf('data:') === 0;
    var needsToLogin = needsToLoad || url == resolve('/login.html');
    if (needsToLogin) {
      if (needsToLoad) {
        browser.get(resolve('/login.html'));
      }
      var login = browser.findElement(by.name('login'));
      login.clear();
      login.sendKeys('admin');
      var password = browser.findElement(by.name('password'));
      password.clear();
      password.sendKeys('admin');
      var button = browser.findElement(by.name('image'));
      button.click();
    }
  });
}

function logout() {
  var browser = global.browser;
  return browser.get(resolve('/logout.html'));
}

function expectPageOk() {
  // Check that the page is a KARL page and not 404, 500
  var browser = global.browser;
  expect(browser.isElementPresent(by.id('karl-app-url'))).to.eventually.be.true;
}

function expectPageNotOk() {
  // Check that the page is a KARL page and not 404, 500
  var browser = global.browser;
  expect(browser.isElementPresent(by.id('karl-app-url'))).to.eventually.be.false;
}


var testGlobals = {
  // ovverride jasmine's expect with chai's
  expect: chai.expect,
  // Helpers to be available from all tests
  resolve: resolve,
  loginAsAdmin: loginAsAdmin,
  logout: logout,
  expectPageOk: expectPageOk,
  expectPageNotOk: expectPageNotOk
};

function onPrepare() {
  var browser = protractor.getInstance();
  _.assign(global, testGlobals, {
    // add browser variable
    browser: browser
  });
  // disable angular syncing
  browser.ignoreSynchronization = true;
}

module.exports = _.assign({}, testGlobals, {
  onPrepare: onPrepare
});
