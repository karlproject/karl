
/* jshint node: true */
'use strict';

var _ = require('lodash');
var multiGlob = require('multi-glob');
var converter = require('selenium-html-js-converter');

multiGlob.glob([
  'karl/seleniumtests/login/*.html',
  //'karl/seleniumtests/blog/*.html',
  'karl/seleniumtests/calendar/*.html',
  'karl/seleniumtests/community/*.html',
  //'karl/seleniumtests/files/*.html',
  //'karl/seleniumtests/forums/*.html',
  'karl/seleniumtests/offices/*.html',
  //'karl/seleniumtests/profiles/*.html',
  'karl/seleniumtests/search/*.html',
  'karl/seleniumtests/tagging/*.html',
  'karl/seleniumtests/wiki/*.html',
], {}, function (er, files) {
  console.log('files:', files);
  _.each(files, function(file) {
    var outFile = file.substring(0, file.length - 4) + 'tmp.js';
    console.log(file, outFile);
    converter.convertHtmlFileToJsFile(file, outFile);
  });
});
