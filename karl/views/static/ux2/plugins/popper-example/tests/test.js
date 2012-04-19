
module('popper-example', {

    setup: function() {
        var self = this;
        $('#main').append(
            '<div id="the-node">The Node Text</div>'
        );
    },

    teardown: function() {
        $('#main').empty();
    }

});


test("Create / destroy", function() {

    $('#the-node').example({
    });

    $('#the-node').example('destroy');

});


test("Changes label", function() {

    $('#the-node').example({
    });
    equal($('#the-node').text(), 'Hello World!');

    $('#the-node').example('destroy');
    equal($('#the-node').text(), 'The Node Text');

});


test("Label option", function() {

    $('#the-node').example({
        label: 'Bottlecap is awesome!'
    });
    equal($('#the-node').text(), 'Bottlecap is awesome!');

    $('#the-node').example('destroy');
    equal($('#the-node').text(), 'The Node Text');

});

