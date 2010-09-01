
(function($){

//
// wiring of tinyMCE editors
//

$(document).ready(function() {

    // See if the wiki plugin needs to be enabled.
    var widget_data = window.karl_client_data && karl_client_data.text || {};
    var plugins = 'paste,embedmedia,spellchecker';
    if (widget_data.enable_wiki_plugin) {
        plugins += ',wicked';
        // Imagedrawer is default enabled on wiki pages.
        // Disabled everywhere else. XXX TODO
        plugins += ',imagedrawer';
    }
     
    // Url that contains the context prefix 
    var here_url = $('#karl-here-url')[0].content;
    // the root url of the tinymce tree
    var tinymce_url = $('#karl-static-url')[0].content + '/tinymce/3.3.8';

    // initialize the editor widget(s)
    $('.mceEditor').tinysafe({
        // All css and js is loaded statically, in our setup.
        // The followings make sure that tinymce does not interfere.
        load_js: false,
        load_editor_css: false,
        script_url: tinymce_url,
        //
        theme: 'advanced',
        skin: 'karl',
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
        paste_create_paragraphs : false,
        paste_create_linebreaks : false,
        paste_use_dialog : false,
        paste_auto_cleanup_on_paste : true,
        paste_convert_middot_lists : true,
        paste_unindented_list_class : "unindentedList",
        paste_convert_headers_to_strong : true,
        theme_advanced_toolbar_location: 'top',
        theme_advanced_buttons1: 'formatselect, bold, italic, bullist, numlist, link, code, removeformat, justifycenter, justifyleft,justifyright, justifyfull, indent, outdent, image, embedmedia, addwickedlink, delwickedlink, spellchecker',
        theme_advanced_buttons2: '',
        theme_advanced_buttons3: '',
        plugins: plugins,
        extended_valid_elements: "object[classid|codebase|width|height],param[name|value],embed[quality|type|pluginspage|width|height|src|wmode|swliveconnect|allowscriptaccess|allowfullscreen|seamlesstabbing|name|base|flashvars|flashVars|bgcolor],script[src]",
        relative_urls : false,
        forced_root_block : 'p',
        spellchecker_rpc_url: "/tinymce_spellcheck",
        spellchecker_languages : "+English=en",
        // options for imagedrawer
        imagedrawer_dialog_url: here_url + 'drawer_dialog_view.html',
        imagedrawer_upload_url: here_url + 'drawer_upload_view.html',
        imagedrawer_data_url: here_url + 'drawer_data_view.html'
    });  

});

})(jQuery);
