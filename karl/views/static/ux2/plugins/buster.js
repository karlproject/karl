
/* Currently, this is experimental. */

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

