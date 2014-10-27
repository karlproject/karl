
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

var testGlobals = {
  // ovverride jasmine's expect with chai's
  expect: chai.expect,
  // Helpers to be available from all tests
  resolve: resolve
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
