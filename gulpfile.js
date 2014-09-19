
/* jshint node: true */
'use strict';

var _ = require('lodash'),
    gulp = require('gulp'),
    util = require('gulp-util'),
    concat = require('gulp-concat'),
    uglify = require('gulp-uglify');

var res = require('./resources.json');
var minPrefix = res.staticPrefix + 'min/';

var print = require('gulp-print');

function staticPaths(items) {
  return _.map(items, function(name) {
    return res.staticPrefix + name;
  })
}

gulp.task('process-js', function () {
  var name = 'karl-ui';
  gulp.src(staticPaths(res.js[name]))
    .pipe(print())
    .pipe(concat(name + '.min.js'))
    .pipe(uglify())
    .pipe(gulp.dest(minPrefix));
  util.log('Producing', util.colors.green(minPrefix + name + '.min.js'));
});

gulp.task('install', ['process-js']);
