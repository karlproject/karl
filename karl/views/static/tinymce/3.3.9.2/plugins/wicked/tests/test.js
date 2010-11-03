
(function($){

var log = function() {
    if (window.console && console.log) {
        // log for FireBug or WebKit console
        console.log(Array.prototype.slice.call(arguments));
    }
};

var endswith = function(s, end, comment) {
    equals(s.substr(s.length - end.length), end, comment);
};


module("tiny.wicked", {

    setup: function() {
        this.timeouts = new MockTimeouts();
        this.timeouts.start();

        $('.mceEditor').tinysafe({
            // static loading
            load_js: false,
            script_url: '../../..',

            theme: 'advanced',
            height: '400',
            width: '550',
            gecko_spellcheck : false,
            theme_advanced_toolbar_location: 'top',
            theme_advanced_buttons1: 'formatselect, bold, italic, bullist, numlist, link, code, removeformat, justifycenter, justifyleft,justifyright, justifyfull, indent, outdent, addwickedlink, delwickedlink',
            theme_advanced_buttons2: '',
            theme_advanced_buttons3: '',
            plugins: 'wicked',
            extended_valid_elements: "object[classid|codebase|width|height],param[name|value],embed[quality|type|pluginspage|width|height|src|wmode|swliveconnect|allowscriptaccess|allowfullscreen|seamlesstabbing|name|base|flashvars|flashVars|bgcolor],script[src]",
            forced_root_block : 'p'
        });

        // one timed event.
        equals(this.timeouts.length, 1, 'timed event ok');
        this.timeouts.execute(0);
        
        this.timeouts.stop();

        tinymce.activeEditor.focus();
        // Repaint the editor
        // This is very important: without this, some interactive
        // actions (such as selection ranges) cannot be simulated.
        tinymce.execCommand('mceRepaint');
    },

    teardown: function() {
    },

    // sets a selection for the testing
    // within a single paragraph node
    // and returns the textual content.
    setSelection: function(node, start, end) {
        var ed = tinymce.activeEditor;
        var sel = ed.selection;
        var dom = ed.dom;

        // find a given character in broken up text nodes
        var findit = function(node, index) {
            var foundNode;
            $.each($(node)[0].childNodes, function(n, textNode) {
                if (textNode.nodeType == 3) {
                    var txt = textNode.nodeValue;
                    if (index <= txt.length) {
                        // found it
                        foundNode = textNode;
                        return false;
                    }
                    index -= txt.length;
                }
            });
            return [foundNode, index];
        };
        // sets the new range
        var rng = dom.createRng();
        rng.setStart.apply(rng, findit(node, start));
        rng.setEnd.apply(rng, findit(node, end));
        sel.setRng(rng);
        // returns the content for checking
        var txt = sel.getContent();
        return txt;
    }

});


test("Create", function() {
    // editor created
    var textarea = $('.mceEditor').eq(0);
    var editor_id = textarea.attr('id');
    ok(editor_id, 'has generated the editor id');
    equals($('#' + editor_id + '_parent').length, 1, 'has generated the editor structure');
});

test("has buttons", function() {
    var buttons = $('.mceButton')

    // add button
    var add_button = buttons.eq(buttons.length - 2);
    endswith(add_button.find('img').attr('src'),
        '/images/addwicked.gif', 'add button ok');
    ok(add_button.hasClass('mceButtonDisabled'), 'add button disabled initially');

    // del button
    var del_button = buttons.eq(buttons.length - 1);
    endswith(del_button.find('img').attr('src'),
        '/images/delwicked.gif', 'del button ok');
    ok(del_button.hasClass('mceButtonDisabled'), 'del button disabled initially');
});

test("add button disabled on no-selection", function() {
    var ed = tinymce.activeEditor;
    var buttons = $('.mceButton')
    var add_button = buttons.eq(buttons.length - 2);
    var del_button = buttons.eq(buttons.length - 1);
    ok(add_button.hasClass('mceButtonDisabled'), 'add button disabled initially');
    ok(del_button.hasClass('mceButtonDisabled'), 'del button disabled initially');

    var editor_content = $('iframe').contents().find('body').children();
    
    // click does not work
    add_button.simulate('click');
    equals(ed.getContent(), '<p>Pellentesque in sagittis ante. Ut porttitor sollicitudin fringilla. Proin sed eros tortor, nec luctus risus! Curabitur adipiscing ullamcorper convallis. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos.</p>',
        'wiki link marker not added');

    // button is disabled, but explicit command also does nothing.
    ed.execCommand('isoAddWicked');

    equals(ed.getContent(), '<p>Pellentesque in sagittis ante. Ut porttitor sollicitudin fringilla. Proin sed eros tortor, nec luctus risus! Curabitur adipiscing ullamcorper convallis. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos.</p>',
        'wiki link marker not added');

});


test("add button works", function() {
    var ed = tinymce.activeEditor;
    var buttons = $('.mceButton')
    var add_button = buttons.eq(buttons.length - 2);
    var del_button = buttons.eq(buttons.length - 1);
    ok(add_button.hasClass('mceButtonDisabled'), 'add button disabled initially');
    ok(del_button.hasClass('mceButtonDisabled'), 'del button disabled initially');

    var editor_content = $('iframe').contents().find('body').children();

    // select a word
    equals(this.setSelection(editor_content.eq(0), 34, 43), 'porttitor', 'full word selected');
    // allow editor to redraw the toolbar
    ed.nodeChanged();

    ok(! add_button.hasClass('mceButtonDisabled'), 'add button enabled');
    ok(del_button.hasClass('mceButtonDisabled'), 'del button stays disabled');

    add_button.simulate('click');

    equals(ed.getContent(), '<p>Pellentesque in sagittis ante. Ut ((porttitor)) sollicitudin fringilla. Proin sed eros tortor, nec luctus risus! Curabitur adipiscing ullamcorper convallis. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos.</p>',
        'wiki link marker added');
    ok(add_button.hasClass('mceButtonDisabled'), 'add button disabled back');

});

test("del button works", function() {
    var ed = tinymce.activeEditor;
    var buttons = $('.mceButton')
    var add_button = buttons.eq(buttons.length - 2);
    var del_button = buttons.eq(buttons.length - 1);
    ok(add_button.hasClass('mceButtonDisabled'), 'add button disabled initially');
    ok(del_button.hasClass('mceButtonDisabled'), 'del button disabled initially');

    var editor_content = $('iframe').contents().find('body').children();

    // select a word
    equals(this.setSelection(editor_content.eq(0), 34, 43), 'porttitor',
        'full word selected');
    // allow editor to redraw the toolbar
    ed.nodeChanged();
    // change it to a wiki link markup
    ed.selection.setContent('((porttitor))');
    equals(this.setSelection(editor_content.eq(0), 34, 47), '((porttitor))',
        'full wiki link selected');
    // allow editor to redraw the toolbar
    ed.nodeChanged();

    ok(add_button.hasClass('mceButtonDisabled'), 'add button stays disabled');
    ok(! del_button.hasClass('mceButtonDisabled'), 'del button enabled');

    del_button.simulate('click');

    equals(ed.getContent(), '<p>Pellentesque in sagittis ante. Ut porttitor sollicitudin fringilla. Proin sed eros tortor, nec luctus risus! Curabitur adipiscing ullamcorper convallis. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos.</p>',
        'wiki link marker removed');
    ok(del_button.hasClass('mceButtonDisabled'), 'del button disabled back');

});

test("del button does not work if no-link is selected", function() {
    var ed = tinymce.activeEditor;
    var buttons = $('.mceButton')
    var add_button = buttons.eq(buttons.length - 2);
    var del_button = buttons.eq(buttons.length - 1);
    ok(add_button.hasClass('mceButtonDisabled'), 'add button disabled initially');
    ok(del_button.hasClass('mceButtonDisabled'), 'del button disabled initially');

    var editor_content = $('iframe').contents().find('body').children();

    // select a word
    equals(this.setSelection(editor_content.eq(0), 34, 43), 'porttitor', 'full word selected');
    // allow editor to redraw the toolbar
    ed.nodeChanged();
    // change it to a wiki link markup
    ed.selection.setContent('po ((rttitor)');
    equals(this.setSelection(editor_content.eq(0), 34, 47), 'po ((rttitor)', 'not a wiki link');
    // allow editor to redraw the toolbar
    ed.nodeChanged();

    ok(! add_button.hasClass('mceButtonDisabled'), 'add button gets enaabled');
    ok(del_button.hasClass('mceButtonDisabled'), 'del button stays disabled');

    del_button.simulate('click');

    // nothing happened
    equals(ed.getContent(), '<p>Pellentesque in sagittis ante. Ut po ((rttitor) sollicitudin fringilla. Proin sed eros tortor, nec luctus risus! Curabitur adipiscing ullamcorper convallis. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos.</p>',
        'nothing happened');

    // button is disabled, but explicit command also does nothing.
    ed.execCommand('isoDelWicked');
    equals(ed.getContent(), '<p>Pellentesque in sagittis ante. Ut po ((rttitor) sollicitudin fringilla. Proin sed eros tortor, nec luctus risus! Curabitur adipiscing ullamcorper convallis. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos.</p>',
        'nothing happened');
});


})(jQuery);

