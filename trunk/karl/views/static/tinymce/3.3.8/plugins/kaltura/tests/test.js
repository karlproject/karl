
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


module("tiny.kaltura", {

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
            theme_advanced_buttons1: 'formatselect, bold, italic, bullist, numlist, link, code, removeformat, justifycenter, justifyleft, justifyright, justifyfull, indent, outdent, kaltura',
            theme_advanced_buttons2: '',
            theme_advanced_buttons3: '',
            plugins: 'kaltura',
            extended_valid_elements: "object[classid|codebase|width|height],param[name|value],embed[quality|type|pluginspage|width|height|src|wmode|swliveconnect|allowscriptaccess|allowfullscreen|seamlesstabbing|name|base|flashvars|flashVars|bgcolor],script[src]",
            forced_root_block : 'p'
        });

        // one timed event.
        equals(this.timeouts.length, 1);
        this.timeouts.execute(0);
        
        this.timeouts.stop();

        tinymce.activeEditor.focus();
        // Repaint the editor
        // This is very important: without this, some interactive
        // actions (such as selection ranges) cannot be simulated.
        tinymce.execCommand('mceRepaint');
    },

    teardown: function() {
    }

});


test("Create", function() {
    var textarea = $('.mceEditor').eq(0);
    var editor_id = textarea.attr('id');
    ok(editor_id, 'editor is present');
    equals($('#' + editor_id + '_parent').length, 1, 'it has a parent');
});

test("has button", function() {
    //we have the button
    endswith($('.mceButton').last().find('img').attr('src'),
        '/images/interactive_video_button.gif', 'there is a kaltura button');
});


})(jQuery);

