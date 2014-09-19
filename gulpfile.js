
/* jshint node: true */
'use strict';

var _ = require('lodash'),
    gulp = require('gulp'),
    util = require('gulp-util'),
    concat = require('gulp-concat'),
    uglify = require('gulp-uglify'),
    header = require('gulp-header');

var res = require('./resources.json');

var banner =  '/*\n * KARL <%= path %> resources generated at <%= new Date().toISOString() %>\n*/\n';

function staticPaths(items) {
  return _.map(items, function(name) {
    return res.staticPrefix + name;
  })
}

gulp.task('process-js', function () {
  var name = 'karl-ui';
  var path = name + '.min.js';
  gulp.src(staticPaths(res.js[name]))
    .pipe(concat(path))
    //.pipe(uglify())
    .pipe(header(_.template(banner, {path: path})))
    .pipe(gulp.dest(res.minPrefix));
  util.log('Producing', util.colors.green(res.minPrefix + path));
});

gulp.task('install', ['process-js']);
