
(function($){

var log = function() {
    if (window.console && console.log) {
        // log for FireBug or WebKit console
        console.log(Array.prototype.slice.call(arguments));
    }
};


module("tinymce karl skin", {

    setup: function() {
        this.timeouts = new MockTimeouts();
        this.timeouts.start();

        $('.mceEditor').tinysafe({
            // static loading
            load_js: false,
            script_url: '../../../../..',

            theme: 'advanced',
            skin: 'karl',
            height: '400',
            width: '550',
            gecko_spellcheck : false,
            theme_advanced_toolbar_location: 'top',
            theme_advanced_buttons1: 'formatselect, bold, italic, bullist, numlist, link, code, removeformat, justifycenter, justifyleft,justifyright, justifyfull, indent, outdent',
            theme_advanced_buttons2: '',
            theme_advanced_buttons3: '',
            plugins: '',
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

});


test("Create", function() {
    // editor created
    var textarea = $('.mceEditor').eq(0);
    var editor_id = textarea.attr('id');
    ok(editor_id, 'has generated the editor id');
    equals($('#' + editor_id + '_parent').length, 1, 'has generated the editor structure');
});


})(jQuery);

