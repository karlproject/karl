
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

var tinymceVersion = '3.5.2';

var rootPath = '../../';
var libs = {};

var pluginsLib = 'ux2/plugins/';
var testLib = pluginsLib + 'testlib/';
var tinymcePluginsLib = 'tinymce-plugins/';
var tinymceLib = 'tinymce/' + tinymceVersion + '/jscripts/tiny_mce/';

libs.jquery = [
    // Workaround jQuery / Sinon
    testLib + 'jquery-animation-workaround.js',
    // Load jQuery and the UI widget factory
    testLib + 'jquery-1.7.1.min.js',
    testLib + 'jquery.ui.widget.js'
];

libs.jqueryUi = [
    // Workaround jQuery / Sinon
    testLib + 'jquery-animation-workaround.js',
    // Load jQuery and jQuery UI
    testLib + 'jquery-1.7.1.min.js',
    testLib + 'jquery-ui-1.9m5.min.js'
];

libs.tinymce = [
    tinymceLib + 'tiny_mce_src.js',
    tinymceLib + 'themes/advanced/editor_template_src.js',
    'ux2/tinymce/jquery.tinysafe.js'
];

libs.testHelpers = [
    testLib + 'json2.js',
    testLib + 'jquery.simulate.js'
];

var extensions = [require('buster-qunit')];

config["popper.example"] = {
    rootPath: rootPath,
    environment: "browser",
    libs: [].concat(libs.jquery, libs.testHelpers),
    sources: [
        pluginsLib + 'popper-example/popper.example.js'
    ],
    tests: [
        pluginsLib + 'popper-example/tests/test.js'
    ],
    extensions: extensions
};

config["popper.tagbox"] = {
    rootPath: rootPath,
    environment: "browser",
    libs: [].concat(libs.jqueryUi, libs.testHelpers),
    sources: [
        pluginsLib + 'popper-tagbox/popper.tagbox.js'
    ],
    tests: [
        pluginsLib + 'popper-tagbox/tests/test.js'
    ],
    extensions: extensions
};

config["popper.pushdown"] = {
    rootPath: rootPath,
    environment: "browser",
    libs: [].concat(libs.jqueryUi, libs.testHelpers),
    sources: [
        pluginsLib + 'popper-pushdown/popper.pushdown.js'
    ],
    tests: [
        pluginsLib + 'popper-pushdown/tests/test.js'
    ],
    extensions: extensions
};

config["tinymce.wicked"] = {
    rootPath: rootPath,
    environment: "browser",
    libs: [].concat(libs.jquery, libs.tinymce, libs.testHelpers),
    sources: [
        tinymcePluginsLib + 'wicked/editor_plugin_src.js',
        tinymcePluginsLib + 'wicked/langs/en.js'
    ],
    tests: [
        tinymcePluginsLib + 'wicked/tests/test.js'
    ],
    extensions: extensions
};

config["tinymce.imagedrawer"] = {
    rootPath: rootPath,
    environment: "browser",
    libs: [].concat(libs.jqueryUi, libs.tinymce, libs.testHelpers, [
        'karl-plugins/karl-buttonset/karl.buttonset.js',
        'karl-plugins/karl-multistatusbox/karl.multistatusbox.js',
        'karl-plugins/karl-slider/karl.slider.js'
    ]),
    sources: [
        tinymcePluginsLib + 'imagedrawer/editor_plugin_src.js',
        tinymcePluginsLib + 'imagedrawer/langs/en.js'
    ],
    tests: [
        tinymcePluginsLib + 'imagedrawer/tests/test.js'
    ],
    extensions: extensions
};

/*
 * XXX broken, because the way we fetch the html snippet
 *
config["tinymce.imagedrawer notiny"] = {
    rootPath: rootPath,
    environment: "browser",
    libs: [].concat(libs.jqueryUi, libs.testHelpers, [
        'karl-plugins/karl-buttonset/karl.buttonset.js',
        'karl-plugins/karl-multistatusbox/karl.multistatusbox.js',
        'karl-plugins/karl-slider/karl.slider.js'
    ]),
    sources: [
        tinymcePluginsLib + 'imagedrawer/editor_plugin_src.js',
        tinymcePluginsLib + 'imagedrawer/langs/en.js'
    ],
    tests: [
        tinymcePluginsLib + 'imagedrawer/tests/test_tiny.imagedrawerinfopanel.js'
    ],
    extensions: extensions
};
*/

config["tinymce.kaltura"] = {
    rootPath: rootPath,
    environment: "browser",
    libs: [].concat(libs.jquery, libs.tinymce, libs.testHelpers, [
        tinymcePluginsLib + 'kaltura/js/swfobject.js'
    ]),
    sources: [
        tinymcePluginsLib + 'kaltura/editor_plugin_src.js',
        tinymcePluginsLib + 'kaltura/langs/en.js'
    ],
    tests: [
        tinymcePluginsLib + 'kaltura/tests/test.js'
    ],
    extensions: extensions
};

