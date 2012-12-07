
(function() {
    tinymce.create('tinymce.plugins.wicked', {

        init : function(ed, url) {
            var t = this;
            t.editor = ed;
            t.url = url;

            // Register commands
            ed.addCommand('isoAddWicked', t.isoAddWicked, t);
            ed.addCommand('isoDelWicked', t.isoDelWicked, t);

            // Register node change handler
            ed.onNodeChange.add(function(ed, cm, n, co) {
                    t.handleNodeChange(ed, cm, n, co);
                }); 

            // Register buttons
            ed.addButton('addwickedlink', {
                    title : 'wicked.addwicked_desc',
                    cmd : 'isoAddWicked',
                    image: t.url + '/images/addwicked.gif'});
            ed.addButton('delwickedlink', {
                    title : 'wicked.delwicked_desc',
                    cmd : 'isoDelWicked',
                    image: t.url + '/images/delwicked.gif'});

        },

        getInfo : function getInfo() {
            return {
                longname : 'Wicked plugin',
                author : 'Balazs Ree <ree@greenfinity.hu>',
                authorurl : '',
                infourl : '',
                version : "1.1"
                };
        },

        re_wikilink: /^\(\(.*?\)\)$/,

        //
        // Node change handler
        //

        handleNodeChange : function handleNodeChange(ed, cm, n, co) {
            var sel = ed.selection;
            // See if we have a selection.
            if (! sel.isCollapsed()) {
                // Check if the selection exactly contains
                // a wiki link (( ... ))
                var selectedText = sel.getContent();
                if (this.re_wikilink.test(selectedText)) {
                    // Selection is a wiki link.
                    // Disable add and enable del button.
                    cm.setDisabled('addwickedlink', true); 
                    cm.setDisabled('delwickedlink', false); 
                } else {
                    // Selection is not wiki link.
                    // Enable add and disable del button.
                    cm.setDisabled('addwickedlink', false); 
                    cm.setDisabled('delwickedlink', true); 
                }
            } else {
                // No selection. Disable both buttons.
                cm.setDisabled('addwickedlink', true); 
                cm.setDisabled('delwickedlink', true);
            }
            return true;
        },
       
        //
        // Commands
        //
        isoAddWicked: function isoAddWicked(cmd, ui, val) {
            var ed = this.editor;
            var sel = ed.selection;
            // See if we have a selection.
            if (! sel.isCollapsed()) {
                // Set new value for the selection.
                var selectedText = sel.getContent();
                sel.setContent('((' + selectedText + '))');
            }
        },

        isoDelWicked: function isoDelWicked(cmd, ui, val) {
            var ed = this.editor;
            var sel = ed.selection;
            // See if we have a selection.
            if (! sel.isCollapsed()) {
                // Check if the selection exactly contains
                // a wiki link (( ... ))
                var selectedText = sel.getContent();
                if (this.re_wikilink.test(selectedText)) {
                    // Set new value for the selection.
                    sel.setContent(selectedText.slice(2, -2));
                }
            }
        }

    });

    // Register plugin
    tinymce.PluginManager.add('wicked', tinymce.plugins.wicked);
    tinymce.PluginManager.requireLangPack('wicked');

})();
