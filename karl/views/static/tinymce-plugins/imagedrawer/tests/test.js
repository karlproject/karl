/*jslint undef: true, newcap: true, nomen: false, white: true, regexp: true */
/*jslint plusplus: false, bitwise: true, maxerr: 50, maxlen: 110, indent: 4 */
/*jslint sub: true */
/*globals window navigator document setTimeout $ */
/*globals sinon module test ok equal deepEqual */
/*globals tinymce */


module("tiny.imagedrawer", {

    setup: function () {
        var self = this;
        $('<textarea id="editor1" name="text" rows="1" cols="40" >Pellentesque in sagittis ante.' +
          ' Ut porttitor ' +
          'sollicitudin fringilla. Proin sed eros tortor, nec luctus risus! Curabitur adipiscing ' +
          'ullamcorper ' +
          'convallis. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos ' +
          'himenaeos.' +
          '</textarea>').appendTo('#main');

        
        this.clock = sinon.useFakeTimers();
        this.clock.tick(5000);

        var initOnce = false;
        $('.mceEditor').tinysafe({
            // static loading
            load_js: false,
            load_editor_css: false,
            content_css: '',
            script_url: '../../../tinymce/3.5.2/jscripts/tiny_mce',
            oninit : function (ed) {
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
            theme_advanced_buttons1: 'formatselect, bold, italic, bullist, numlist, link, ' +
                'code, removeformat, justifycenter, justifyleft,justifyright, justifyfull, ' +
                'indent, outdent, image',
            theme_advanced_buttons2: '',
            theme_advanced_buttons3: '',
            plugins: '', //'imagedrawer',
            extended_valid_elements: 'object[classid|codebase|width|height],param[name|value],' +
                'embed[quality|type|pluginspage|width|height|src|wmode|swliveconnect|allowscriptaccess' +
                '|allowfullscreen|seamlesstabbing|name|base|flashvars|flashVars|bgcolor],script[src]',
            forced_root_block : 'p',
            // options for imagedrawer
            imagedrawer_dialog_url: 'drawer_dialog_view.html',
            imagedrawer_upload_url: 'drawer_upload_view.html',
            imagedrawer_data_url: 'drawer_data_view.html',
            imagedrawer_enable_upload: true
        });
    },

    onInit: function (ed) {
        this.ed = ed;
        ed.focus();
        ed.execCommand('mceRepaint');
    },

    teardown: function () {
        this.clock.restore();
        // make sure to kill a stale popup / overlay
        $('#main').empty();
        var killfromhere = function (me) {
            if (me.length > 0) {
                killfromhere(me.next());
                me.remove();
            }
        };
        killfromhere($('#main').next());
    }

    /*
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
    */

});


test("Create", function () {
    console.log('test Create begin');
    // editor created
    var textarea = $('.mceEditor').eq(0);
    var editor_id = textarea.attr('id');
    ok(editor_id, 'has generated the editor id');
    equal($('#' + editor_id + '_parent').length, 1, 'has generated the editor structure');
    console.log('test Create end');
});


test("has button", function() {
    console.log('test Has button begin');
    var buttons = $('.mceButton')

    // add button
    var image_button = buttons.eq(buttons.length - 1);
    ok(image_button.find('span').hasClass('mce_image'), 'image button ok');
    ok(! image_button.hasClass('mceButtonDisabled'), 'image button ensabled');
    console.log('test Has button end');

});

/*
test("popup", function() {
    var buttons = $('.mceButton')
    var image_button = buttons.eq(buttons.length - 1);

    // click button
    image_button.simulate('click');
    
    equal($('.tiny-imagedrawer-dialog').length, 1, 'popup activated');

});

test("close button", function() {
    $('.mceButton').last().simulate('click');
    equal($('.tiny-imagedrawer-dialog').length, 1, 'popup activated');

    // click close
    $('.tiny-imagedrawer-button-close').find('span').simulate('click');

    // XXX TODO test with animation.
    ///ok($('.tiny-imagedrawer-dialog').is(':hidden'), 'popup deactivated');

});

*/




