
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


module("tiny.spellchecker", {

    setup: function() {
        var self = this;

        // Mock ajax.
        this.server = new MoreMockHttpServer();
        this.server.handle = this.handle_ajax;
        this.server.start();
        
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
            theme_advanced_buttons1: 'formatselect, bold, italic, bullist, numlist, link, code, removeformat, justifycenter, justifyleft,justifyright, justifyfull, indent, outdent, spellchecker',
            theme_advanced_buttons2: '',
            theme_advanced_buttons3: '',
            plugins: 'spellchecker',
            extended_valid_elements: "object[classid|codebase|width|height],param[name|value],embed[quality|type|pluginspage|width|height|src|wmode|swliveconnect|allowscriptaccess|allowfullscreen|seamlesstabbing|name|base|flashvars|flashVars|bgcolor],script[src]",
            forced_root_block : 'p',
            // Options for spellchecker
            spellchecker_rpc_url: "/tinymce_spellcheck",
            spellchecker_languages : "+English=en"
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
        this.server.stop();
        $('#main').empty();
    },
 
    handle_ajax: function(request, ajax_heartbeat) {

        //log(request.urlParts);
        if (request.urlParts.file == 'tinymce_spellcheck') {
         
            // Return the example response from the server.
            // This is just enough to test the bare minimum.
            // We need to evolve this as we add more tests.
            //
            request.setResponseHeader("Content-Type", "application/json; charset=UTF-8");
            request.receive(200,  JSON.stringify({
                "result": ["risus", "sagittis", "nostra", "sed", 
                        "litora", "eros", "fringilla", "torquent", 
                        "nec", "convallis", "adipiscing", "Curabitur", 
                        "luctus", "himenaeos", "Ut", "aptent", "taciti", 
                        "ullamcorper", "inceptos", "Proin", "porttitor", 
                        "tortor", "sollicitudin", "sociosqu", 
                        "Pellentesque", "conubia"
                        ],
                "id": null,
                "error": null
            }));
        } else {
            request.receive(404, 'Not Found in Mock Server');
        }

    }

});


test("Create", function() {
    // editor created
    var textarea = $('#editor1').eq(0);
    var editor_id = textarea.attr('id');
    ok(editor_id, 'has generated the editor id');
    equal($('#' + editor_id + '_parent').length, 1, 'has generated the editor structure');
});

test("has button", function() {
    var spell_button = $('.mceSplitButton').last();
    ok(spell_button.hasClass('mceSplitButton mceSplitButtonEnabled mce_spellchecker'),
                'spell button found');
});


/* TODO: fix, rewrite with sinon's mock http.
 *
test("clicking the button does something", function() {
    var spell_button = $('.mceSplitButton').last();
    var ed = tinymce.activeEditor;
    var editor_content = $('iframe').contents().find('body').children();

    // do the ajax
    spell_button.find('a span').eq(0).simulate('click');

    // spinner does some timing,which we execute.
    this.clock.tick(1000);

    // XXX no idea yet, what to check here...
    //
    // TODO continue the saga.
    ok(true);

});
*/


})(jQuery);

