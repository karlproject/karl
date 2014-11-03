#! /usr/local/bin/node

var converter = require('selenium-html-js-converter');
converter.convertHtmlFileToJsFile('karl/seleniumtests/login/login_admin.html', 'karl/seleniumtests/login/login_admin.js');
converter.convertHtmlFileToJsFile('karl/seleniumtests/community/make_community.html', 'karl/seleniumtests/community/make_community.js');
