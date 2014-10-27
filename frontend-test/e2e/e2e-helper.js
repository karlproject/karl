
/* jshint expr: true, node: true, globalstrict: true */
'use strict';

var chai = require('chai');
var chaiAsPromised = require('chai-as-promised');
chai.use(chaiAsPromised);
var expect = chai.expect;
var _ = require('lodash');
var protractor = require('protractor');
var by = protractor.By;

var testGlobals = {
  // ovverride jasmine's expect with chai's
  expect: chai.expect
  // Helpers to be available from all tests
  // (... add as needed)
};

function onPrepare() {
  _.assign(global, testGlobals, {
    // add browser variable
    browser: protractor.getInstance()
  });
}

module.exports = _.assign({}, testGlobals, {
  onPrepare: onPrepare
});
