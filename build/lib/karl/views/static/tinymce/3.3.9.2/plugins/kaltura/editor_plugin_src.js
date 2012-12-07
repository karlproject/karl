/**
 *
 * @author Moxiecode
 * @copyright Copyright © 2004-2008, Moxiecode Systems AB, All rights reserved.
 *
 * @copyright Copyright (C) 2010 Open Society Institute
 * @author Thomas Moroz: tmoroz@sorosny.org
 *
 */

(function() {

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

    tinymce.create('tinymce.plugins.Kaltura', {
        /**
         * Initializes the plugin, this will be executed after the plugin has been created.
         * This call is done before the editor instance has finished it's initialization so use the onInit event
         * of the editor instance to intercept that event.
         *
         * @param {tinymce.Editor} ed Editor instance that the plugin is initialized in.
         * @param {string} url Absolute URL to where the plugin is located.
         */
        init : function(ed, url) {
            var self = this;
            var t = this;
            this._url = url
            this.editor = ed;

            this.entry_ids = [];

            ed.onInit.add(function() {
                //ed.dom.loadCSS(url + "/css/ui.css");
            });
            function isMedia(n) {
                // XXX Need to check if this is a kaltura resource!
                return /^mceItemFlash$/.test(n.className);
            }; 
            
             // Register commands
            ed.addCommand('mceKaltura', function() {
                log('button pressed');

                var callback = function(success, session_key) {
                    if (success) {

                        log('We have a session', session_key);
                        self.session_key = session_key;
                        self.flashVars = {
                            uid: self.local_user,
                            partnerId: self.partner_id,
                            ks: session_key,
                            afterAddEntry: '_onContributionWizardAddEntry',
                            close: '_onContributionWizardClose',
                            showCloseButton: true,
                            Permissions: 1
                        };
                        window._onContributionWizardAddEntry = function(entries) {self._onContributionWizardAddEntry(entries);},
                        window._onContributionWizardClose = function() {self._onContributionWizardClose();},

                        // delete the old entry
                        this.entry_ids = [];
                        self._createDialog();
                        self.dialog.dialog('open');
                    } else {
                        alert('Session creation failed');
                    }
                };

                self._requestKalturaSession(callback);

                log('session requested');
                
            });

            // Register buttons
            ed.addButton('kaltura', {
                title : 'kaltura.kaltura_button_desc',
                image: url+ '/images/interactive_video_button.gif',
                cmd : 'mceKaltura'
            });


            ed.onNodeChange.add(function(ed, cm, n) {
                    cm.setActive('kaltura', n.nodeName == 'IMG' && isMedia(n));
            });

            ed.onInit.add(function() {

                    if (ed.settings.content_css !== false)
                            ed.dom.loadCSS(url + "/css/content.css");
                  
                    if (ed && ed.plugins.contextmenu) {
                            ed.plugins.contextmenu.onContextMenu.add(function(th, m, e) {
                                    if (e.nodeName == 'IMG' && /mceItemFlash/.test(e.className)) {
                                            m.add({title : 'media.edit', icon : 'media', cmd : 'mceEmbedMedia'});
                                    }
                            });
                    }
            });

            ed.onBeforeSetContent.add(function(ed, o) {
                var snippet = t.newEmbedSnippet();
                var html = o.content;
                var shtml = snippet._objectsToSpans(html);
                o.content = shtml;
            }, t);

            ed.onSetContent.add(function() {
                var content = $(ed.getBody());

                content.find('span.mceItemEmbed,span.mceItemObject').each(function() {
                    var embed = $(this);
                    // If we are an embed inside an object, do not process
                    if (embed.is('span.mceItemEmbed') && embed.parent().is('span.mceItemObject')) {
                        return;
                    }
                    // Do the transformation

                    var snippet = t.newEmbedSnippet();
                    var embed_shtml;
                    if ($.browser.msie) {
                        embed_shtml = embed[0].outerHTML;
                    } else {
                        var wrapper = $('<div />');
                        wrapper.append(embed.clone());
                        embed_shtml = wrapper[0].innerHTML;
                        wrapper.remove();
                    }
                    var embed_text = snippet._spansToObjects(embed_shtml);

                    var result = $('<img />')
                        .attr('src', t.url + '/images/trans.gif')
                        .addClass('mceItemFlash')
                        .addClass('mceMarker-embedmedia')
                        .attr('title', embed_text)
                        .attr('width', embed.attr('width'))
                        .attr('height', embed.attr('height'));
                        //.attr('align', f.align.options[f.align.selectedIndex].value);
                    // XXX for some reason, this serialization is essential on IE
                    result = $('<div />').append(result).html();
                    embed.replaceWith(result);
                });
                content.find('span.mceEndObject').remove();

            });

            function getAttr(s, n) {
                    n = new RegExp(n + '=\"([^\"]+)\"', 'g').exec(s);

                    return n ? ed.dom.decode(n[1]) : '';
            };

            ed.onPostProcess.add(function(ed, o) {
                o.content = o.content.replace(/<img[^>]+>/g, function(img) {
                    var cl = getAttr(img, 'class');
                    // this class is never removed
                    if (cl == 'mceMarker-embedmedia') {
                        // update width, height
                        var snippet = t.newEmbedSnippet();
                        snippet.setContent(getAttr(img, 'title'));
                        snippet.setParms({
                            width: getAttr(img, 'width'),
                            height: getAttr(img, 'height')
                        });
                        img = snippet.getContent();
                        snippet.wrapper.remove();
                    }
                    return img;
                });
            });

        },
            

        newEmbedSnippet : function() {
            // manipulation of embed snippets
            // created here because at this point we have jquery
            // for sure.

            var EmbedSnippet = function EmbedSnippet() {};
            $.extend(EmbedSnippet.prototype, {

                _objectsToSpans : function(str) {
                    str = str.replace(/<object([^>]*)>/gi, '<span class="mceItemObject"$1>');
                    str = str.replace(/<embed([^>]*)\/?>/gi, '<span class="mceItemEmbed"$1></span>');
                    str = str.replace(/<embed([^>]*)>/gi, '<span class="mceItemEmbed"$1>');
                    str = str.replace(/<\/(object)([^>]*)>/gi, '<span class="mceEndObject"></span></span>');
                    str = str.replace(/<\/embed>/gi, '');
                    str = str.replace(/<param([^>]*)\/?>/gi, '<span class="mceItemParam"$1></span>');
                    str = str.replace(/<\/param>/gi, '');
                    return str;
                },

                _spansToObjects : function(str) {
                    str = str.replace(/<span([^>]*) class="?mceItemParam"?([^>]*)><\/span>/gi, '<param$1 $2></param>');
                    str = str.replace(/<span([^>]*) class="?mceItemEmbed"?([^>]*)><\/span>/gi, '<embed$1 $2></embed>');
                    str = str.replace(/<span([^>]*) class="?mceItemObject"?([^>]*)>/gi, '<object$1 $2>');
                    str = str.replace(/<span class="?mceEndObject"?><\/span><\/span>/gi, '</object>');
                    return str;
                },

                setContent: function(html) {
                    this.wrapper = $('<div />');
                    var wrapper = this.wrapper;
                    var shtml = this._objectsToSpans(html);
                    wrapper[0].innerHTML = shtml;

                    this.root = wrapper.children();
                    var root = this.root;
                    // detect type
                    this.emtype = null;
                    if (root.is('span.mceItemObject')) {
                        var inside = root.find('span.mceItemEmbed');
                        if (inside) {
                            this.emtype = 'object+embed';
                            this.inside = inside;
                            // remove bad attributes. (Important: 
                            // will explode flash if left in)
                            if (inside.attr('mce_src')) {
                                inside.removeAttr('mce_src');
                            }
                        }

                        // Fix missing params (broken in IE8, kaltura)
                        var params = ['allowScriptAccess', 'allowNetworking', 'allowFullScreen',
                            'bgcolor', 'movie', 'flashVars'];
                        var to_add = [];
                        $.each(params, function(i, value) {
                            var found = false;
                            root.find('span.mceItemParam').each(function(i, elem) {
                                a = $(elem).attr('name');
                                if (a == value || a == value.toLowerCase()) {
                                    found = true;
                                    return false;
                                }
                            });
                            if (! found) {
                                // Is there an attr?
                                if (root.attr(value)) {
                                    to_add.push({k: value, v: root.attr(value)});
                                } else if (root.attr(value.toLowerCase())) {
                                    to_add.push({k: value, v: root.attr(value.toLowerCase())});
                                } else if (value == 'movie') {
                                    // special handling of resource
                                    if (root.attr('resource')) {
                                        to_add.push({k: value, v: root.attr('resource')});
                                    }
                                }
                            }
                        });
                        $.each(to_add, function(i, value) {
                            try {
                            $('<span class="mceItemParam"></span>')
                                .attr('name', value.k)
                                .attr('value', value.v)
                                .prependTo(root);
                            } catch(e) {}
                        });
                    }

                    // remove bad attributes. (Important: 
                    // will explode flash if left in)
                    if (root.attr('mce_src')) {
                        root.removeAttr('mce_src');
                    }
                    // cascade
                    return this;
                },

                getContent: function() {
                    var shtml = this.wrapper.html();
                    var html = this._spansToObjects(shtml);
                    return html;
                },

                getParms: function() {
                    return {
                        width: this.root.attr('width'),
                        height: this.root.attr('height')
                    };
                },

                setParms: function(parms) {
                    if (this.emtype == 'object+embed') {
                        parms.width && this.root.attr('width', parms.width); 
                        parms.height && this.root.attr('height', parms.height); 
                        parms.width && this.inside.attr('width', parms.width); 
                        parms.height && this.inside.attr('height', parms.height); 
                    } else {
                        parms.width && this.root.attr('width', parms.width); 
                        parms.height && this.root.attr('height', parms.height); 
                    }
                    return this;
                }

            });
            // give access to the class from the popup
            this.newEmbedSnippet = function newEmbedSnippet() {
                return new EmbedSnippet();   
            };
            return this.newEmbedSnippet();
        },

        getJQuery: function() {
            return window.jQuery;
        },


        _requestKalturaSession: function(callback) {
            var self = this;

            // Do we have a session already?
            if (this.session_key) {
                // Yes, so return it.
                callback(true, this.session_key);
            } else {
                // Create session directly from the client.
                // XXX TODO: create session from the server with ajax. 
                this.partner_id = this.editor.getParam('kaltura_partner_id');
                this.sub_partner_id =  this.editor.getParam('kaltura_sub_partner_id');
                var user_secret = this.editor.getParam('kaltura_user_secret', '');
                var admin_secret = this.editor.getParam('kaltura_admin_secret', '');
                var session_url = this.editor.getParam('kaltura_session_url', '');
                this.local_user = this.editor.getParam('kaltura_local_user', 'ANONYMOUS');
                var session_url = this.editor.getParam('kaltura_session_url', '');
                this.kcw_uiconf_id = this.editor.getParam('kaltura_kcw_uiconf_id', '1000741');
                this.player_uiconf_id = this.editor.getParam('kaltura_player_uiconf_id', '');
                this.player_cache_st = this.editor.getParam('kaltura_player_cache_st', '');
                var is_admin = true; // XXX should come from the server ?

                if (session_url) {
                    //server session
                    log('Start server session');
                    $.ajax({
                        url: session_url,
                        success: function(json) {
                            if (json.error) {
                                log('Ajax returned error', json);
                                callback(false);
                            } else {
                                // pipe to the passed callback.
                                callback(true, json.result.ks);
                            }
                        },
                        error: function(json, status, e) {
                            log('Ajax failed', json, status, e);
                            callback(false);
                        }
                    });
                } else {
                    //client session
                    log('Start client session');
                    var kc = new KalturaConfiguration(Number(this.partner_id));
                    var client = new KalturaClient(kc);
                    this.session = new KalturaSessionService(client);
                    this.session.start(function(success, session_key) {
                            if (success) {
                                log('session created', session_key);
                                self.session_key = session_key;
                            }
                            // pipe to the passed callback.
                            callback(success, session_key);
                        },
                        is_admin && admin_secret || user_secret,
                        self.local_user,
                        is_admin && KalturaSessionType.ADMIN || KalturaSessionType.USER,
                        self.partner_id,
                        undefined, undefined);
                }
            }
        },

        _createDialog: function() {
            if (! this.dialog) {
                this.dialog = $('<div id="tiny-kaltura-kcw"></div>');
                this.dialog.hide().appendTo('body');
                this.dialog.dialog({
                    // the next options are adjustable if the style changes
                    // Full width is computed from width border and padding.
                    // IE's quirkmode is also taken to consideration.
                    //width: 6 + 390 + 7 + 320 + 6 + (jQuery.boxModel ? 0 : 10), // ?? XXX
                    width: 680,
                    dialogClass: 'tiny-kaltura-dialog',
                    // the next options are mandatory for desired behaviour
                    autoOpen: false,
                    modal: true,
                    bgiframe: true,    // XXX bgiFrame is currently needed for modal
                    hide: 'fold'
                });
                // remove these classes from the dialog. This is to avoid
                // the outside border that this class adds by default.
                // Instead we add our own panel, with the advantage that
                // sizes can be set correctly even on IE.
                // XXX actually one problem is that we get rid of the header,
                // and the component does not really support this oob.
                var dialog_parent = this.dialog
                    .css('border', '0')
                    .css('padding', '0')
                    .css('overflow', 'hidden')
                    .parents('.ui-dialog');
                dialog_parent
                        //.removeClass('ui-dialog-content ui-widget-content')
                        .removeClass('ui-dialog-content')
                        .css('overflow', 'hidden');
                // We need a close button. For simplicity, we just move the
                // close button from the header here, since it's already wired
                // up correctly.
                dialog_parent.find('.ui-dialog-titlebar-close').eq(0)
                    .appendTo(this.dialog.find('.tiny-imagedrawer-panel-top'))
                    .removeClass('ui-dialog-titlebar-close')
                    .addClass('tiny-imagedrawer-button-close');

                // add the flash
                //
                //Prepare variables to be passed to embedded flash object.
                //swfobject.embedSWF "http://www.kaltura.com/kcw/ui_conf_id/1000199", 
                var so = new SWFObject('http://www.kaltura.com/kcw/ui_conf_id/' + this.kcw_uiconf_id, 'kcw',
                    "680", "360", "9.0.0", "#FFFFFF");
                so.addParam('allowScriptAccess', 'always');
                so.addParam('allowNetworking', 'all');
                so.addParam('wmode', "opaque");
                $.each(this.flashVars, function(key, value) {
                    so.addVariable(key, value);
                });
                so.useExpressInstall('expressInstall.swf');
                so.write('tiny-kaltura-kcw');
            }
        },

        _onContributionWizardAddEntry: function(entries) {
            log(entries.length + " media file/s was/were successfully uploaded");
            for(var i = 0; i < entries.length; i++) {
                log("entries["+i+"]:EntryID = " + entries[i].entryId);
                log("entries["+i+"]:",  entries[i]);
                this.entry_ids.push(entries[i].entryId);
            }
        },

        _onContributionWizardClose: function() {
            var self = this;

            this.dialog.dialog('close');
            log("closed Kaltura Contribution Wizard");

            if (this.entry_ids.length == 0) {
                log("No entry.");
                return;
            }

            //var width = 400;
            //var height = 333;
            //var align = 'left';
            
            log("Will insert videos #:", this.entry_ids.length);
            $.each(this.entry_ids, function(i) {
                if (i > 0) {
                    self.editor.execCommand('mceInsertContent', false, '<br>');
                }
                var entry_id = this;
                log("Inserting entry id", entry_id, i);

                self._insertMedia({
                    entry_id: entry_id
                });
            });
            this.editor.execCommand('mceRepaint');
            log('Success with insertion.');

        },


        /**
         * Creates control instances based in the incoming name. This method is normally not
         * needed since the addButton method of the tinymce.Editor class is a more easy way of adding buttons
         * but you sometimes need to create more complex controls like listboxes, split buttons etc then this
         * method can be used to create those.
         *
         * @param {String} n Name of the control to create.
         * @param {tinymce.ControlManager} cm Control manager to use inorder to create new control.
         * @return {tinymce.ui.Control} New control instance or null if no control was created.
         */
        createControl : function(n, cm) {
            return null;
        },


        _makeKalturaMarkup: function(parms) {

            // parms:
            //   entry_id
            //   width
            //   height

            // title
            parms.width = parms.width || 400;
            parms.height = parms.height || 333;

            var markup = '<object' +
                'id="kaltura_player"' +
                'name="kaltura_player"' +
                'type="application/x-shockwave-flash"' +
                'allowfullscreen="true"' +
                'allownetworking="all"' +
                'allowscriptaccess="always"' +
                'xmlns:dc="http://purl.org/dc/terms/"' +
                'xmlns:media="http://search.yahoo.com/searchmonkey/media/"' +
                'rel="media:video"' +
                'resource="http://www.kaltura.com/index.php/kwidget/cache_st/' + this.player_cache_st + '/wid/_' + this.partner_id + '/uiconf_id/' + this.player_uiconf_id + '/entry_id/' + parms.entry_id + '"' +
                'data="http://www.kaltura.com/index.php/kwidget/cache_st/' + this.player_cache_st + '/wid/_' + this.partner_id + '/uiconf_id/' + this.player_uiconf_id + '/entry_id/' + parms.entry_id + '"' +
                'height="' + parms.height + '"' +
                'width="' + parms.width + '">' +

                '<param name="allowFullScreen" value="true">' +
                '<param name="allowNetworking" value="all">' +
                '<param name="allowScriptAccess" value="always">' +
                '<param name="bgcolor" value="#000000">' +
                '<param name="flashVars" value="&amp;">' +
                '<param name="movie" value="http://www.kaltura.com/index.php/kwidget/cache_st/' + this.player_cache_st + '/wid/_' + this.partner_id + '/uiconf_id/' + this.player_uiconf_id + '/entry_id/' + parms.entry_id + '">' +
                '<a href="http://corp.kaltura.com">video platform</a>' +
                '<a href="http://corp.kaltura.com/video_platform/video_management">video management</a>' +
                '<a href="http://corp.kaltura.com/solutions/video_solution">video solutions</a>' +
                '<a href="http://corp.kaltura.com/video_platform/video_publishing">video player</a>' +
                '<a rel="media:thumbnail" href="http://cdnbakmi.kaltura.com/p/' + this.partner_id + '/sp/' + this.sub_partner_id + '/thumbnail/entry_id/' + parms.entry_id + '/width/120/height/90/bgcolor/000000/type/2"></a>' +

                //'<span property="dc:description" content="' + parms.title + '"></span>' +
                //'<span property="media:title" content="' + parms.title + '"></span>' +
                '<span property="media:width" content="' + parms.width + '"></span>' +
                '<span property="media:height" content="' + parms.height + '"></span>' +
                '<span property="media:type" content="application/x-shockwave-flash"></span>' +

            '</object>';

            return markup;

        },

        _insertMedia: function(_parms) {

            var markup = this._makeKalturaMarkup(_parms);

            // update snippet
            var snippet = this.newEmbedSnippet();
            snippet
                .setContent(markup);

            var parms = snippet.getParms();
            //if (! parms.width) parms.width = 400;
            //if (! parms.height) parms.height = 333;


            var result = $('<img />')
                .attr('src', this._url + '/images/trans.gif')
                .addClass('mceItemFlash')
                .addClass('mceMarker-embedmedia')
                .attr('title', snippet.getContent())
                .attr('width', parms.width)
                .attr('height', parms.height);
                //.attr('align', f.align.options[f.align.selectedIndex].value);
            h = $('<div />').append(result).html();

            
            log('Will insert:', h);

            this.editor.execCommand('mceInsertContent', false, h);
            //this.editor.execCommand('mceRepaint');
        },


        /**
         * Returns information about the plugin as a name/value array.
         * The current keys are longname, author, authorurl, infourl and version.
         *
         * @return {Object} Name/value array containing information about the plugin.
         */
        getInfo : function() {
            return {
                longname : 'All in One Video Pack',
                author : 'Kaltura',
                authorurl : 'http://www.kaltura.com',
                infourl : 'http://corp.kaltura.com',
                version : "1.0"
            };
        }
        



    });
    
    // Register plugin
    tinymce.PluginManager.add('kaltura', tinymce.plugins.Kaltura);
    tinymce.PluginManager.requireLangPack('kaltura');

})();
