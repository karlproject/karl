
(function($){

$(document).ready(function() {


    var server = new MoreMockHttpServer(function(request) {

        if (request.urlParts.file == 'tinymce_spellcheck') {
         
            // XXX This is very dumb, just a copy of the
            // example response from the server. We could
            // be much smarter here :) and at least attempt
            // to simulate the server a bit more.
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

    });

    server.start();

    $('.mceEditor').tinysafe({
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
        spellchecker_languages : "+English=en",

    });

    $('.preview-button').click(function() {
        // insert into preview area
        $('#preview-area')
            .empty()
            .append(tinymce.activeEditor.getContent());
    });

});

})(jQuery);

