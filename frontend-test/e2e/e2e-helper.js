
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
var loginInfo = require('./login-info.json');


// Create a logger that works in promises
// Example usage:
//
//      browser.getCurrentUrl().then(qlog('url'));
//
function qlog(name) {
  return function() {
    var args = Array.prototype.slice.call(arguments);
    args.splice(0, 0, _.template('QLOG [<%= name %>]', {name: name}));
    console.log.apply(null, args);
  };
}

function resolve(path) {
  var browser = global.browser;
  // make sure path is added _relative_ to the site
  return browser.baseUrl + path;
}

function loginAsAdmin() {
  // this logs in only if needed, so it can be
  // safely used as beforeEach.
  var browser = global.browser;
  var testUser = loginInfo.testUser;
  return browser.getCurrentUrl().then(function(url) {
    var needsToLoad = url.indexOf('data:') === 0;
    // if we need to load, we will need to login later
    var needsToLogin = needsToLoad || url.indexOf(resolve('/login.html')) === 0;
    if (needsToLoad) {
      browser.get(resolve('/login.html'));
    }
    if (needsToLogin) {
      var login = browser.findElement(by.name('login'));
      login.clear();
      login.sendKeys(testUser.username);
      var password = browser.findElement(by.name('password'));
      password.clear();
      password.sendKeys(testUser.password);
      var button = browser.findElement(by.name('image'));
      button.click();
    }
  });
}

function logout() {
  var browser = global.browser;
  return browser.get(resolve('/logout.html'));
}

function expectPageNotLogin() {
  // use containment because of the parameters attached to the end.
  var browser = global.browser;
  expect(browser.getCurrentUrl()).to.eventually.not.have.string(resolve('/login.html'));
}

function expectPageOk() {
  // Check that the page is a KARL page and not 404, 500
  var browser = global.browser;
  expect(browser.isElementPresent(by.id('karl-app-url'))).to.eventually.be.true;
  expectPageNotLogin();
}

function expectPageError() {
  // Check that the page is a 404, 500, and not a KARL page or the login page.
  var browser = global.browser;
  expect(browser.isElementPresent(by.id('karl-app-url'))).to.eventually.be.false;
  expectPageNotLogin();
}


var testGlobals = {
  // ovverride jasmine's expect with chai's
  expect: chai.expect,
  // Helpers to be available from all tests
  qlog: qlog,
  resolve: resolve,
  loginAsAdmin: loginAsAdmin,
  logout: logout,
  expectPageOk: expectPageOk,
  expectPageError: expectPageError,
  expectPageNotLogin: expectPageNotLogin,
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
