/**
 * $Id: editor_plugin_src.js 1037 2009-03-02 16:41:15Z spocke $
 *
 * @author Moxiecode
 * @copyright Copyright © 2004-2008, Moxiecode Systems AB, All rights reserved.
 */

(function() {
	var each = tinymce.each;

	tinymce.create('tinymce.plugins.EmbedMediaPlugin', {
		init : function(ed, url) {
			var t = this;
			t.editor = ed;
			t.url = url;

			function isMedia(n) {
				return /^mceItemFlash$/.test(n.className);
			};

			// Register commands
			ed.addCommand('mceEmbedMedia', function() {
				ed.windowManager.open({
					file : url + '/media.htm',
					width : 480 + parseInt(ed.getLang('embedmedia.delta_width', 0)),
					height : 500 + parseInt(ed.getLang('embedmedia.delta_height', 0)),
					inline : 1
				}, {
					plugin_url : url
				});
			});

			// Register buttons
			ed.addButton('embedmedia', {title : 'media.desc', cmd : 'mceEmbedMedia'});

			ed.onNodeChange.add(function(ed, cm, n) {
				cm.setActive('embedmedia', n.nodeName == 'IMG' && isMedia(n));
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

			ed.onSetContent.add(function() {
                            var content = $(ed.getBody());
                            content.find('embed,object').each(function() {
                                var embed = $(this);
                                // If we are an embed inside an object, do not process
                                if (embed.is('embed') && embed.parent().is('object')) {
                                    return;
                                }
                                // Do the transformation
                                var embed_text = $('<div />').append(embed.clone()).html();
                                var result = $('<img />')
                                    .attr('src', t.url + '/img/trans.gif')
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

                        setContent: function(html) {
                            this.wrapper = $('<div />');
                            var wrapper = this.wrapper;
                            wrapper.append(html);
                            this.root = wrapper.children();
                            var root = this.root;
                            // detect type
                            this.emtype = null;
                            if (root.is('object')) {
                                var inside = root.find('embed');
                                if (inside) {
                                    this.emtype = 'object+embed';
                                    this.inside = inside;
                                    // remove bad attributes. (Important: 
                                    // will explode flash if left in)
                                    if (inside.attr('mce_src')) {
                                        inside.removeAttr('mce_src');
                                    }
                                }
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
                            return this.wrapper.html();
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

		getInfo : function() {
			return {
				longname : 'Media',
				author : 'Moxiecode Systems AB',
				authorurl : 'http://tinymce.moxiecode.com',
				infourl : 'http://wiki.moxiecode.com/index.php/TinyMCE:Plugins/media',
				version : tinymce.majorVersion + "." + tinymce.minorVersion
			};
		}

	});

	// Register plugin
	tinymce.PluginManager.add('embedmedia', tinymce.plugins.EmbedMediaPlugin);
})();
