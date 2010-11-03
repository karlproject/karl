
(function($){

var log = function() {
    if (window.console && console.log) {
        // log for FireBug or WebKit console
        console.log(Array.prototype.slice.call(arguments));
    }
};


module("tiny.paste", {

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
            theme_advanced_buttons1: 'formatselect, bold, italic, bullist, numlist, link, code, removeformat, justifycenter, justifyleft,justifyright, justifyfull, indent, outdent',
            theme_advanced_buttons2: '',
            theme_advanced_buttons3: '',
            plugins: 'paste',
            extended_valid_elements: "object[classid|codebase|width|height],param[name|value],embed[quality|type|pluginspage|width|height|src|wmode|swliveconnect|allowscriptaccess|allowfullscreen|seamlesstabbing|name|base|flashvars|flashVars|bgcolor],script[src]",
            forced_root_block : 'p',
            // parameters for paste plugin
            paste_create_paragraphs : false,
            paste_create_linebreaks : false,
            paste_use_dialog : false,
            paste_auto_cleanup_on_paste : true,
            paste_convert_middot_lists : true,
            paste_unindented_list_class : "unindentedList",
            paste_convert_headers_to_strong : true
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
                    if (index < txt.length) {
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

// XXX Here we would simulate specific real life paste samples
// (for example 'HTML' originating from MS Word, etc.)
// and check what output is produced from them by the plugin.

})(jQuery);

