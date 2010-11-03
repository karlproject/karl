
(function($){

$(document).ready(function() {

    $('.mceEditor').tinysafe({
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

    $('.preview-button').click(function() {
        // insert into preview area
        $('#preview-area')
            .empty()
            .append(tinymce.activeEditor.getContent());
    });

});

})(jQuery);

