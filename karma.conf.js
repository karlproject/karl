
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
      [
        // Stuff needed for the old contentfeeds test
        //
        //  Workaround prelude to make jquery animations work with sinon.clock
        //  (Must come before jquery)
        'karl/views/static/karl-plugins/karl-js/tests/obsolete-testlibs/jquery-animation-workaround.js',
      ],
      // The javacript sources
      jsBundle('karl-ui'),
      jsBundle('karl-multifileupload'),
      jsBundle('tinymce-3.5.2.karl'),
      jsBundle('karl-wikitoc'),
      jsBundle('karl-contentfeeds'),
      // (we do not need to load tinymce-popup-utils here,
      // as it only gets included from tinymce popup pages)
      jsBundle('karl-custom'),
      [
        //
        // libraries needed for the tests
        'frontend-test/unit/helper/qunit-asserts.js',
        'node_modules/lodash/lodash.js',
        'karl/views/static/**/*-spec.js',
        'karl/views/static/**/*-fixture.html',
        // Stuff needed for the old contentfeeds test
        //
        // testing goodies
        'karl/views/static/karl-plugins/karl-js/tests/obsolete-testlibs/sinon-1.3.1.js',
        'karl/views/static/karl-plugins/karl-js/tests/obsolete-testlibs/sinon-ie-1.3.1.js',
        'karl/views/static/karl-plugins/karl-js/tests/obsolete-testlibs/jquery.simulate.js',
        // This test uses some stuff we don't use in new tests -->
        'karl/views/static/karl-plugins/karl-js/tests/obsolete-testlibs/mock.js',
        'karl/views/static/karl-plugins/karl-js/tests/obsolete-testlibs/moremockhttp.js',
        'karl/views/static/karl-plugins/karl-js/tests/obsolete-testlibs/mocktimeouts_pre.js',
        'karl/views/static/karl-plugins/karl-js/tests/obsolete-testlibs/mocktimeouts.js',
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
