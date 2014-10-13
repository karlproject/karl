
var res = require('./karl/views/static/resources.json');
var _ = require('lodash');

function staticPaths(items) {
  return _.map(items, function(name) {
    return res.staticPrefix + name;
  });
}

function jsBundle(name) {
  return staticPaths(res.js[name]);
}

module.exports = function(config) {
  config.set({
    // base path is set back to project root
    basePath: '.',
    files: Array.prototype.concat(
      jsBundle('karl-ui'),
      jsBundle('karl-multifileupload'),
      jsBundle('tinymce-3.5.2.karl'),
      jsBundle('karl-wikitoc'),
      // (we do not need to load tinymce-popup-utils here,
      // as it only gets included from tinymce popup pages)
      jsBundle('karl-custom'),
      [
        'frontend-test/unit/helper/qunit-asserts.js',
        'karl/views/static/**/*-spec.js',
        'karl/views/static/**/*-fixture.html',
      ]
    ),
    browsers: ['PhantomJS'],
    preprocessors: {
      '**/*.html': ['html2js'],
      '**/*.json': ['html2js'],
    },
    // Use only ports here that are forwarded by Sauce Connect tunnel.
    // Check usable ports on http://saucelabs.com/docs/connect.
    port: 5050,
    frameworks: ['mocha', 'detectBrowsers', 'chai'],
    reporters: ['progress', 'junit'],
    junitReporter: {
      // this path is relative from the basePath
      outputFile: 'log/unit-test-results.xml',
      suite: 'frontend-unit'
    },
    autoWatch: false,
    singleRun: true,
    colors: true,
    // logLevel: config.LOG_DEBUG,
    detectBrowsers: {
      enabled: false,
    },
    customLaunchers: {
    },
  });
};
