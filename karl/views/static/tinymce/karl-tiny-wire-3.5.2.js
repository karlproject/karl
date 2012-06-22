(function($){

//
// wiring of tinyMCE editors
//

$(document).ready(function() {

    // See if the wiki plugin needs to be enabled.
    var widget_data = window.karl_client_data && karl_client_data.text || {};
    var kaltura_data = window.karl_client_data && karl_client_data.kaltura || {};
    var plugins = 'paste,embedmedia,spellchecker,imagedrawer,advimagescale,advlist,print,table,autosave';
    if (widget_data.enable_wiki_plugin) {
        plugins += ',wicked';
    }
    if (kaltura_data.enabled) {
        plugins += ',kaltura';
    }

    // Url that contains the context prefix
    var here_url = $('#karl-here-url')[0].content;
    // the root url of the tinymce tree
    var static_url = $('#karl-static-url')[0].content;
    var tinymce_url = static_url + '/tinymce/3.5.2/jscripts/tiny_mce';
    var tinymce_plugins_url = static_url + '/tinymce-plugins';
    // The root url of Karl
    var app_url = $("#karl-app-url").eq(0).attr('content');

    // Load our local plugins (needed, because they are not
    // under the tinymce tree)
    $.each(['advimagescale', 'embedmedia', 'imagedrawer', 'kaltura', 'wicked'], function(index, plugin_name) {
        tinymce.PluginManager.load(plugin_name, tinymce_plugins_url + '/' + plugin_name + '/');
    });
    tinymce.ThemeManager.load('advanced', tinymce_plugins_url + '/' + 'theme-advanced-3.5.2/editor_template_src.js');



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
        height: 400,
        width: 550,
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
        theme_advanced_buttons1: 'bold, italic, underline, |, forecolor, backcolor, removeformat, |, bullist, numlist, |, justifycenter, justifyleft,justifyright, justifyfull, |, indent, outdent, |, image, embedmedia, kaltura, |, print',
        theme_advanced_buttons2: 'formatselect, fontselect, fontsizeselect, |, blockquote, hr, |, link, addwickedlink, delwickedlink, code, spellchecker, restoredraft',
        theme_advanced_buttons3: '',
        theme_advanced_toolbar_align : "center",
        theme_advanced_statusbar_location : false,
        plugins: plugins,
        extended_valid_elements: "object[classid|codebase|width|height],param[name|value],embed[quality|type|pluginspage|width|height|src|wmode|swliveconnect|allowscriptaccess|allowfullscreen|seamlesstabbing|name|base|flashvars|flashVars|bgcolor],script[src]",
        relative_urls : false,
        forced_root_block : 'p',
        spellchecker_rpc_url: app_url + "/tinymce_spellcheck",
        spellchecker_languages : "+English=en",
        // options for imagedrawer
        imagedrawer_dialog_url: here_url + 'drawer_dialog_view.html',
        imagedrawer_upload_url: here_url + 'drawer_upload_view.html',
        imagedrawer_data_url: here_url + 'drawer_data_view.html',
        imagedrawer_enable_upload: widget_data.enable_imagedrawer_upload,
        //options for kaltura
        kaltura_partner_id: kaltura_data.partner_id,
        kaltura_sub_partner_id: kaltura_data.sub_partner_id,
        kaltura_local_user: kaltura_data.local_user,
        kaltura_user_secret: kaltura_data.user_secret,
        kaltura_admin_secret: kaltura_data.admin_secret,
        kaltura_kcw_uiconf_id: kaltura_data.kcw_uiconf_id,
        kaltura_player_uiconf_id: kaltura_data.player_uiconf_id,
        kaltura_player_cache_st: kaltura_data.player_cache_st,
        kaltura_session_url: kaltura_data.session_url
    });

    // If there are any submit buttons then they should reset
    // the onbeforeunload, as when we Submit, we want
    // no annoying "Are you sure to leave this page" popup.
    // So this will bust autosave's popup when saving.
    $('.formsubmit .button[type="submit"][name="submit"]').click(function (evt) {
        tinymce.each(tinyMCE.editors, function(ed) {
            ed.isNotDirty = 1; // Force not dirty state (for autosave)
        });
        window.preventUnlock = true; // make sure no unlock will happen
    }); 


});

})(jQuery);
