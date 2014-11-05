
/* jshint node: true */
'use strict';

var _ = require('lodash'),
    path = require('path'),
    gulp = require('gulp'),
    plugins = require('gulp-load-plugins')(),
    util = require('gulp-util'),
    fs = require('fs'),
    karma = require('karma').server;

var res = require('./karl/views/static/resources.json');

var banner =  '/*\n * KARL <%= fullName %> generated resources http://github.com/karlproject/karl %>\n*/\n';
var stampfile =  'KARL resources generated at <%= new Date().toISOString() %>\n';

function staticPaths(items) {
  return _.map(items, function(name) {
    return res.staticPrefix + name;
  });
}

function destPrefix(name) {
  // hardwire tinymce destination from here,
  // as it's simpler than putting it to the json file.
  return name.indexOf('tinymce') === 0 ? res.tinymceMinPrefix : res.minPrefix;
}

function destFolder(name) {
  return res.staticPrefix + destPrefix(name);
}

gulp.task('stamp', function() {
  fs.writeFile(res.staticPrefix + 'dist/stampfile', _.template(stampfile)());
});

gulp.task('copy', function() {
  // jquery from napa
  gulp.src(['./node_modules/jquery/jquery.js'])
    .pipe(gulp.dest(res.staticPrefix + 'dist/jquery/'));
  // jquery-ui from napa
  gulp.src(['./node_modules/jquery-ui/ui/**/*'])
    .pipe(gulp.dest(res.staticPrefix + 'dist/jquery-ui/ui/'));
  gulp.src(['./node_modules/jquery-ui/external/jquery.bgiframe-2.1.2.js'])
    .pipe(gulp.dest(res.staticPrefix + 'dist/jquery-ui/external/'));
  gulp.src(['./node_modules/jquery-ui/themes/base/**/*'])
    .pipe(gulp.dest(res.staticPrefix + 'dist/jquery-ui/themes/base/'));
  // tinymce from napa
  gulp.src(['./node_modules/tinymce/jscripts/**/*'])
    .pipe(gulp.dest(res.staticPrefix + 'dist/tinymce/jscripts/'));
});

gulp.task('process-js', function () {
  _.each(res.js, function(items, name) {
    var fullName = name + '.min.js';
    var dest = destFolder(name);
    gulp.src(staticPaths(items))
      .pipe(plugins.sourcemaps.init())
        .pipe(plugins.concat(fullName))
        .pipe(plugins.removeUseStrict())
        .pipe(plugins.uglify())
        .pipe(plugins.header(_.template(banner, {fullName: fullName})))
      .pipe(plugins.sourcemaps.write('./'))
      .pipe(gulp.dest(dest));
    util.log('Producing', util.colors.green(destFolder(name) + fullName));
  });
});

gulp.task('process-css', function () {
  _.each(res.css, function(name) {
    var fullName = name + '.min.css';
    var dest = destFolder(name);
    gulp.src(res.staticPrefix + name + '.css')
      .pipe(plugins.minifyCss())
      .pipe(plugins.header(_.template(banner, {fullName: fullName})))
      .pipe(plugins.rename({suffix: '.min'}))
      // same dest as src.
      .pipe(gulp.dest(res.staticPrefix));
    util.log('Producing', util.colors.green(res.staticPrefix + fullName));
  });
});

gulp.task('install', ['process-js', 'process-css']);


gulp.task('unit', function (done) {
  karma.start({
    configFile: __dirname + '/karma.conf.js',
    singleRun: true,
    detectBrowsers: {
      enabled: true,
      phantomJs: true,
    },
  }, done);
});

gulp.task('autounit', function (done) {
  karma.start({
    configFile: __dirname + '/karma.conf.js',
    singleRun: false,
    autoWatch: true,
  }, done);
});

gulp.task('e2e', function (done) {
  gulp.src(['./frontend-test/e2e/**/*-scenario.js'])
  .pipe(plugins.protractor.protractor({
    configFile: 'protractor.conf.js',
    args: []
  }))
  .on('error', function(e) {
    throw e;
  });
});

gulp.task('e2e-debug', function (done) {
  gulp.src(['./frontend-test/e2e/**/*-scenario.js'])
  .pipe(plugins.protractor.protractor({
    configFile: 'protractor.conf.js',
    args: ['debug']
  }))
  .on('error', function(e) {
    throw e;
  });
});
gulp.task('install', ['copy', 'process-js', 'process-css', 'stamp']);
