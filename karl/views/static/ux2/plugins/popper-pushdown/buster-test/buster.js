

var config = module.exports;

config["My tests"] = {
    rootPath: "../../",
    environment: "browser", // or "node"
    sources: [
        "testlib/jquery-animation-workaround.js",

        "testlib/jquery-1.6.2.min.js",
        "testlib/jquery.ui.widget.js",

        "popper-pushdown/popper.pushdown.js"
    ],
    tests: [
        "testlib/jquery.simulate.js",
        "testlib/JSON2.js",
        "popper-pushdown/buster-test/popper.pushdown-test.js"
    ]
}

