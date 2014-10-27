
var helper = require('./frontend-test/e2e/e2e-helper.js');

exports.config = {
  specs: ['frontend-test/e2e/**/*-scenario.js'],
  baseUrl: 'http://127.0.0.1:6543/pg/',
  rootElement: 'body',
  onPrepare: helper.onPrepare,
  jasmineNodeOpts: {
    onComplete: function() {},
    isVerbose: true,
    showColors: true,
    includeStackTrace: true,
    defaultTimeoutInterval: 60000,
  },
  chromeDriver: './node_modules/chromedriver/lib/chromedriver/chromedriver',
  seleniumServerJar: 'node_modules/selenium-standalone/.selenium/2.43.1/server.jar'
};
