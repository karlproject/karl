
/* jshint node: true */
'use strict';

var _ = require('lodash'),
    gulp = require('gulp'),
    plugins = require('gulp-load-plugins')(),
    util = require('gulp-util');

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
    var dest = res.staticPrefix + (name.indexOf('tinymce') == 0 ? res.tinymceMinPrefix : res.minPrefix);
    gulp.src(staticPaths(items))
      .pipe(plugins.concat(path))
      .pipe(plugins.uglify())
      .pipe(plugins.header(_.template(banner, {path: path})))
      .pipe(gulp.dest(dest));
    util.log('Producing', util.colors.green(dest + path));
  });
});

gulp.task('install', ['process-js']);
