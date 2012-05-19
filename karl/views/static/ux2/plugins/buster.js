
/* 
 * XXX Currently, this is experimental.
 * TODO Please, correct, and adapt to your OS!
 *
 *
 * - Install Node.js and npm (the Node Package Manager)
 *
 *       ...
 *
 * - Install buster.js::
 *
 *       % sudo npm install -g buster
 *
 * - Install buster-qunit:
 *
 *       % git clone git://github.com/reebalazs/buster-qunit.git
 *
 *       % sudo npm install -g ./buster-qunit
 *
 * - Start a buster server
 *
 *       % buster server
 *
 * - If you have phantom.js installed, capture it with the script provided
 *   by buster. The following path depends on your npm installation.
 *
 *       % phantomjs /opt/local/lib/node_modules/buster/script/phantom.js
 *
 * - Capture as many browsers on http://127.0.0.1:1111/ as you like.
 *
 * - cd to this directory, and run all the tests. Change your code and repeat as you like.
 *
 *       % buster test
 *
 * */

var config = module.exports;

var libs_jquery = [
    // Workaround jQuery / Sinon
    'testlib/jquery-animation-workaround.js',
    // Load jQuery and the UI widget factory
    'testlib/jquery-1.6.2.min.js',
    'testlib/jquery.ui.widget.js'
];

var libs_jquery_ui = [
    // Workaround jQuery / Sinon
    'testlib/jquery-animation-workaround.js',
    // Load jQuery and jQuery UI
    'testlib/jquery-1.6.2-jquery-ui-1.9m5.min.js'
];

var testHelpers = [
    'testlib/json2.js',
    'testlib/jquery.simulate.js'
];

var extensions = [require('buster-qunit')];

config["popper.example"] = {
    rootPath: "./",
    environment: "browser",
    libs: [].concat(libs_jquery, testHelpers),
    sources: [
        'popper-example/popper.example.js'
    ],
    tests: [
        'popper-example/tests/test.js'
    ],
    extensions: extensions
};

config["popper.tagbox"] = {
    rootPath: "./",
    environment: "browser",
    libs: [].concat(libs_jquery_ui, testHelpers),
    sources: [
        'popper-tagbox/popper.tagbox.js'
    ],
    tests: [
        'popper-tagbox/tests/test.js'
    ],
    extensions: extensions
};

config["popper.pushdown"] = {
    rootPath: "./",
    environment: "browser",
    libs: [].concat(libs_jquery_ui, testHelpers),
    sources: [
        'popper-pushdown/popper.pushdown.js'
    ],
    tests: [
        'popper-pushdown/tests/test.js'
    ],
    extensions: extensions
};

