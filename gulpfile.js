
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
  _.each(res.js, function(items, name) {
    var path = name + '.min.js';
    // hardwire tinymce destination from here,
    // as it's simpler than putting it to the json file.
    var dest = name.indexOf('tinymce') == 0 ? res.tinymceMinPrefix : res.minPrefix;
    gulp.src(staticPaths(items))
      .pipe(concat(path))
      .pipe(uglify())
      .pipe(header(_.template(banner, {path: path})))
      .pipe(gulp.dest(dest));
    util.log('Producing', util.colors.green(dest + path));
  });
});

gulp.task('install', ['process-js']);
