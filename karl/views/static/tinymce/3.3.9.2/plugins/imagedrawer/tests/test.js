
(function($){

var log = function() {
    if (window.console && console.log) {
        // log for FireBug or WebKit console
        console.log(Array.prototype.slice.call(arguments));
    }
};


module("tiny.imagedrawer", {

    setup: function() {

        // mock the ajax
        this.server = new MoreMockHttpServer();
        this.server.handle = this.handle_ajax;
        this.server.start();

        // mock the timeouts
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
            theme_advanced_buttons1: 'formatselect, bold, italic, bullist, numlist, link, code, removeformat, justifycenter, justifyleft,justifyright, justifyfull, indent, outdent, image',
            theme_advanced_buttons2: '',
            theme_advanced_buttons3: '',
            plugins: 'imagedrawer',
            extended_valid_elements: "object[classid|codebase|width|height],param[name|value],embed[quality|type|pluginspage|width|height|src|wmode|swliveconnect|allowscriptaccess|allowfullscreen|seamlesstabbing|name|base|flashvars|flashVars|bgcolor],script[src]",
            forced_root_block : 'p',
            // options for imagedrawer
            imagedrawer_dialog_url: 'drawer_dialog_view.html',
            imagedrawer_upload_url: 'drawer_upload_view.html',
            imagedrawer_data_url: 'drawer_data_view.html',
            imagedrawer_enable_upload: true
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
        this.server.stop();
        // make sure to kill a stale popup / overlay
        var killfromhere = function(me) {
            if (me.length > 0) {
                killfromhere(me.next());
                me.remove();
            }
        };
        killfromhere($('#main').next());
    },

    handle_ajax: function(request) {

        if (request.urlParts.file == 'imagedrawer_dialog_snippet.html') {
            // this comes direct from the filesystem.
            // This is in realty done by the server.
            request.bypass();

        } else if (request.urlParts.file == 'drawer_dialog_view.html') {
            // the snippet is coming from a static file,
            // let's grab that and return in an ajax response.
            var snippet = $.ajax({
                async: false,
                url: '../imagedrawer_dialog_snippet.html'
            }).responseText;
         
            request.setResponseHeader("Content-Type", "application/json; charset=UTF-8");
            request.receive(200,  JSON.stringify({
                dialog_snippet: snippet
            }));
        }

    }

});


test("Create", function() {
    // editor created
    var textarea = $('.mceEditor').eq(0);
    var editor_id = textarea.attr('id');
    ok(editor_id, 'has generated the editor id');
    equals($('#' + editor_id + '_parent').length, 1, 'has generated the editor structure');
});


test("has button", function() {
    var buttons = $('.mceButton')

    // add button
    var image_button = buttons.eq(buttons.length - 1);
    ok(image_button.find('span').hasClass('mce_image'), 'image button ok');
    ok(! image_button.hasClass('mceButtonDisabled'), 'image button ensabled');

});

test("popup", function() {
    var buttons = $('.mceButton')
    var image_button = buttons.eq(buttons.length - 1);

    // click button
    image_button.simulate('click');
    
    equals($('.tiny-imagedrawer-dialog').length, 1, 'popup activated');

});

test("close button", function() {
    $('.mceButton').last().simulate('click');
    equals($('.tiny-imagedrawer-dialog').length, 1, 'popup activated');

    // click close
    $('.tiny-imagedrawer-button-close').find('span').simulate('click');

    // XXX TODO test with animation.
    ///ok($('.tiny-imagedrawer-dialog').is(':hidden'), 'popup deactivated');

});




})(jQuery);

