
(function($){

//
// A console.log replacement that works on all browsers
// If the browser does not have a console, it's silent
//
// usage: log('This happened.');
// or:    log('Variables:', var1, var2, var3);
//
var log = function() {
    if (window.console && console.log) {
        // log for FireBug or WebKit console
        console.log(Array.prototype.slice.call(arguments));
    }
};


$(document).ready(function() {

    var server = new MoreMockHttpServer(function(request) {

        log(request.urlParts);
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

    });


    server.start();

    $('.mceEditor').tinysafe({
        theme: 'advanced',
        //skin: 'karl',
        mode: 'specific_textareas',
        height: '400',
        width: '550',
        convert_urls : false,
        gecko_spellcheck : true,
        submit_patch: false,
        entity_encoding: "numeric",
        add_form_submit_trigger: false,
        add_unload_trigger: false,
        strict_loading_mode: true,
        theme_advanced_toolbar_location: 'top',
        theme_advanced_buttons1: 'formatselect, bold, italic, bullist, numlist, link, code, removeformat, justifycenter, justifyleft,justifyright, justifyfull, indent, outdent, image',
        theme_advanced_buttons2: '',
        theme_advanced_buttons3: '',
        plugins: 'imagedrawer',
        extended_valid_elements: "object[classid|codebase|width|height],param[name|value],embed[quality|type|pluginspage|width|height|src|wmode|swliveconnect|allowscriptaccess|allowfullscreen|seamlesstabbing|name|base|flashvars|flashVars|bgcolor],script[src]",
        relative_urls : false,
        forced_root_block : 'p',
        // options for imagedrawer
        imagedrawer_dialog_url: 'drawer_dialog_view.html',
        imagedrawer_upload_url: 'drawer_upload_view.html',
        imagedrawer_data_url: 'drawer_data_view.html',
        imagedrawer_enable_upload: true
    });

    $('.preview-button').click(function() {
        // insert into preview area
        $('#preview-area')
            .empty()
            .append(tinymce.activeEditor.getContent());
    });

});

})(jQuery);

