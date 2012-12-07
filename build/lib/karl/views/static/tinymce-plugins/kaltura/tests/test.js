
(function($){

var log = function() {
    if (window.console && console.log) {
        // log for FireBug or WebKit console
        console.log(Array.prototype.slice.call(arguments));
    }
};

var endswith = function(s, end, comment) {
    equal(s.substr(s.length - end.length), end, comment);
};


module("tiny.kaltura", {

    setup: function() {
        var self = this;
        this.clock = sinon.useFakeTimers();  // Needed, and enough ;)

        $('<textarea id="editor1" name="text" rows="1" cols="40" >Pellentesque in sagittis ante. Ut porttitor' +
            '</textarea>').appendTo('#main');


        var initOnce = false;
        $('#editor1').tinysafe({
            // static loading
            load_js: false,
            script_url: '../../..',
            init_instance_callback : function(ed) {
                if (initOnce) {
                    // prevent init from running twice!!!!
                    return;
                }
                initOnce = true;
                self.onInit(ed);
            },

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
    },
    
    onInit: function(ed) {
        this.ed = ed;
        ed.focus();
        // Repaint the editor
        // This is very important: without this, some interactive
        // actions (such as selection ranges) cannot be simulated.
        ed.execCommand('mceRepaint');
    },

    teardown: function() {
        this.clock.restore();
        $('#main').empty();
    }

});


test("Create", function() {
    var textarea = $('#editor1').eq(0);
    var editor_id = textarea.attr('id');
    ok(editor_id, 'editor is present');
    equal($('#' + editor_id + '_parent').length, 1, 'it has a parent');
});

test("has button", function() {
    //we have the button
    endswith($('.mceButton').last().find('img').attr('src'),
        '/images/interactive_video_button.gif', 'there is a kaltura button');
});


})(jQuery);

