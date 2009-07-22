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

			function isMediaElm(n) {
				return /^(mceItemFlash|mceItemShockWave|mceItemWindowsMedia|mceItemQuickTime|mceItemRealMedia)$/.test(n.className);
			};

                        /*
			ed.onPreInit.add(function() {
				// Force in _value parameter this extra parameter is required for older Opera versions
				ed.serializer.addRules('param[name|value|_mce_value]');
			});
                        */

			// Register commands
			ed.addCommand('mceEmbedMedia', function() {
				ed.windowManager.open({
					file : url + '/media.htm',
					width : 430 + parseInt(ed.getLang('embedmedia.delta_width', 0)),
					height : 470 + parseInt(ed.getLang('embedmedia.delta_height', 0)),
					inline : 1
				}, {
					plugin_url : url
				});
			});

			// Register buttons
			ed.addButton('embedmedia', {title : 'media.desc', cmd : 'mceEmbedMedia'});

			ed.onNodeChange.add(function(ed, cm, n) {
				cm.setActive('embedmedia', n.nodeName == 'IMG' && isMediaElm(n));
			});

			ed.onInit.add(function() {
				var lo = {
					mceItemFlash : 'flash',
					mceItemShockWave : 'shockwave',
					mceItemWindowsMedia : 'windowsmedia',
					mceItemQuickTime : 'quicktime',
					mceItemRealMedia : 'realmedia'
				};

				//ed.selection.onSetContent.add(function() {
				//	t._spansToImgs(ed.getBody());
				//});

				//ed.selection.onBeforeSetContent.add(t._objectsToSpans, t);

				if (ed.settings.content_css !== false)
					ed.dom.loadCSS(url + "/css/content.css");
                              
                                /*
				if (ed.theme.onResolveName) {
					ed.theme.onResolveName.add(function(th, o) {
						if (o.name == 'img') {
							each(lo, function(v, k) {
								if (ed.dom.hasClass(o.node, k)) {
									o.name = v;
									o.title = ed.dom.getAttrib(o.node, 'title');
									return false;
								}
							});
						}
					});
				}
                                */

				if (ed && ed.plugins.contextmenu) {
					ed.plugins.contextmenu.onContextMenu.add(function(th, m, e) {
						if (e.nodeName == 'IMG' && /mceItem(Flash|ShockWave|WindowsMedia|QuickTime|RealMedia)/.test(e.className)) {
							m.add({title : 'media.edit', icon : 'media', cmd : 'mceEmbedMedia'});
						}
					});
				}
			});

			//ed.onBeforeSetContent.add(t._objectsToSpans, t);

			ed.onSetContent.add(function() {
                            var content = $(ed.getBody());
                            content.find('embed').each(function() {
                                var embed = $(this);
                                var embed_text = $('<div />').append(embed.clone()).html();
                                var result = $('<img />')
                                    .attr('src', t.url + '/img/trans.gif')
                                    .addClass('mceItemFlash')
                                    .attr('title', embed_text)
                                    .attr('width', embed.attr('width'))
                                    .attr('height', embed.attr('height'));
                                    //.attr('align', f.align.options[f.align.selectedIndex].value);
                                // XXX for some reason, this serialization is essential on IE
                                result = $('<div />').append(result).html();
                                embed.replaceWith(result);
                            });

			});

                        /*
			ed.onPreProcess.add(function(ed, o) {
				var dom = ed.dom;

				if (o.set) {
                                    alert('set...');
					t._spansToImgs(o.node);

					each(dom.select('IMG', o.node), function(n) {
						var p;

						if (isMediaElm(n)) {
							p = t._parse(n.title);
							dom.setAttrib(n, 'width', dom.getAttrib(n, 'width', p.width || 100));
							dom.setAttrib(n, 'height', dom.getAttrib(n, 'height', p.height || 100));
						}
					});
				    //each(dom.select('IMG', o.node), function(n) {
				}

				if (o.get) {
                                    alert('get...');
				    each(dom.select('IMG', o.node), function(n) {
					if (n.className == 'mceItemFlash') {
                                            var s = '<embed src="http://c.brightcove.com/services/viewer/federated_f8/1125995047" bgcolor="#FFFFFF" flashVars="videoId=29291660001&playerId=1125995047&viewerSecureGatewayURL=https://console.brightcove.com/services/amfgateway&servicesURL=http://services.brightcove.com/services&cdnURL=http://admin.brightcove.com&domain=embed&autoStart=false&" base="http://admin.brightcove.com" name="flashObj" width="486" height="412" seamlesstabbing="false" type="application/x-shockwave-flash" swLiveConnect="true" pluginspage="http://www.macromedia.com/shockwave/download/index.cgi?P1_Prod_Version=ShockwaveFlash"></embed>';
					    $(n).replaceWith(s);
					}
				    });
				}


			});
                        */

                        /*
			ed.onPostProcess.add(function(ed, o) {
				o.content = o.content.replace(/_mce_value=/g, 'value=');
			});
                        */

			function getAttr(s, n) {
				n = new RegExp(n + '=\"([^\"]+)\"', 'g').exec(s);

				return n ? ed.dom.decode(n[1]) : '';
			};

			ed.onPostProcess.add(function(ed, o) {
                            var content = $(o.content);
                            var s = '<embed src="http://c.brightcove.com/services/viewer/federated_f8/1125995047" bgcolor="#FFFFFF" flashVars="videoId=29291660001&playerId=1125995047&viewerSecureGatewayURL=https://console.brightcove.com/services/amfgateway&servicesURL=http://services.brightcove.com/services&cdnURL=http://admin.brightcove.com&domain=embed&autoStart=false&" base="http://admin.brightcove.com" name="flashObj" width="486" height="412" seamlesstabbing="false" type="application/x-shockwave-flash" swLiveConnect="true" pluginspage="http://www.macromedia.com/shockwave/download/index.cgi?P1_Prod_Version=ShockwaveFlash"></embed>';
                            content.find('img').each(function() {
                                var img = $(this);
                                var result = img.attr('title');
                                img.replaceWith(result);
                            });
                            // stringify back content...
                            o.content = $('<div />').append(content).html();
			});

		},

		getInfo : function() {
			return {
				longname : 'Media',
				author : 'Moxiecode Systems AB',
				authorurl : 'http://tinymce.moxiecode.com',
				infourl : 'http://wiki.moxiecode.com/index.php/TinyMCE:Plugins/media',
				version : tinymce.majorVersion + "." + tinymce.minorVersion
			};
		},

		// Private methods
                /*
		_objectsToSpans : function(ed, o) {
			var t = this, h = o.content;

			h = h.replace(/<script[^>]*>\s*write(Flash|ShockWave|WindowsMedia|QuickTime|RealMedia)\(\{([^\)]*)\}\);\s*<\/script>/gi, function(a, b, c) {
				var o = t._parse(c);

				return '<img class="mceItem' + b + '" title="' + ed.dom.encode(c) + '" src="' + t.url + '/img/trans.gif" width="' + o.width + '" height="' + o.height + '" />'
			});

			h = h.replace(/<object([^>]*)>/gi, '<span class="mceItemObject" $1>');
			h = h.replace(/<embed([^>]*)\/?>/gi, '<span class="mceItemEmbed" $1></span>');
			h = h.replace(/<embed([^>]*)>/gi, '<span class="mceItemEmbed" $1>');
			h = h.replace(/<\/(object)([^>]*)>/gi, '</span>');
			h = h.replace(/<\/embed>/gi, '');
			h = h.replace(/<param([^>]*)>/gi, function(a, b) {return '<span ' + b.replace(/value=/gi, '_mce_value=') + ' class="mceItemParam"></span>'});
			h = h.replace(/\/ class=\"mceItemParam\"><\/span>/gi, 'class="mceItemParam"></span>');

			o.content = h;
		},
                */

                /*
		_buildObj : function(o, n) {
			var ob, ed = this.editor, dom = ed.dom, p = this._parse(n.title), stc;
			
			stc = ed.getParam('media_strict', true) && o.type == 'application/x-shockwave-flash';

			p.width = o.width = dom.getAttrib(n, 'width') || 100;
			p.height = o.height = dom.getAttrib(n, 'height') || 100;

			if (p.src)
				p.src = ed.convertURL(p.src, 'src', n);

			if (stc) {
				ob = dom.create('span', {
					id : p.id,
					mce_name : 'object',
					type : 'application/x-shockwave-flash',
					data : p.src,
					style : dom.getAttrib(n, 'style'),
					width : o.width,
					height : o.height
				});
			} else {
				ob = dom.create('span', {
					id : p.id,
					mce_name : 'object',
					classid : "clsid:" + o.classid,
					style : dom.getAttrib(n, 'style'),
					codebase : o.codebase,
					width : o.width,
					height : o.height
				});
			}

			each (p, function(v, k) {
				if (!/^(width|height|codebase|classid|id|_cx|_cy)$/.test(k)) {
					// Use url instead of src in IE for Windows media
					if (o.type == 'application/x-mplayer2' && k == 'src' && !p.url)
						k = 'url';

					if (v)
						dom.add(ob, 'span', {mce_name : 'param', name : k, '_mce_value' : v});
				}
			});

			if (!stc)
				dom.add(ob, 'span', tinymce.extend({mce_name : 'embed', type : o.type, style : dom.getAttrib(n, 'style')}, p));

			return ob;
		},
                */

                /*
		_spansToImgs : function(p) {
			var t = this, dom = t.editor.dom, im, ci;

			each(dom.select('span', p), function(n) {
				// Convert object into image
				if (dom.getAttrib(n, 'class') == 'mceItemObject') {
					ci = dom.getAttrib(n, "classid").toLowerCase().replace(/\s+/g, '');

					switch (ci) {
						case 'clsid:d27cdb6e-ae6d-11cf-96b8-444553540000':
							dom.replace(t._createImg('mceItemFlash', n), n);
							break;

						case 'clsid:166b1bca-3f9c-11cf-8075-444553540000':
							dom.replace(t._createImg('mceItemShockWave', n), n);
							break;

						case 'clsid:6bf52a52-394a-11d3-b153-00c04f79faa6':
						case 'clsid:22d6f312-b0f6-11d0-94ab-0080c74c7e95':
						case 'clsid:05589fa1-c356-11ce-bf01-00aa0055595a':
							dom.replace(t._createImg('mceItemWindowsMedia', n), n);
							break;

						case 'clsid:02bf25d5-8c17-4b23-bc80-d3488abddc6b':
							dom.replace(t._createImg('mceItemQuickTime', n), n);
							break;

						case 'clsid:cfcdaa03-8be4-11cf-b84b-0020afbbccfa':
							dom.replace(t._createImg('mceItemRealMedia', n), n);
							break;

						default:
							dom.replace(t._createImg('mceItemFlash', n), n);
					}
					
					return;
				}

				// Convert embed into image
				if (dom.getAttrib(n, 'class') == 'mceItemEmbed') {
					switch (dom.getAttrib(n, 'type')) {
						case 'application/x-shockwave-flash':
							dom.replace(t._createImg('mceItemFlash', n), n);
							break;

						case 'application/x-director':
							dom.replace(t._createImg('mceItemShockWave', n), n);
							break;

						case 'application/x-mplayer2':
							dom.replace(t._createImg('mceItemWindowsMedia', n), n);
							break;

						case 'video/quicktime':
							dom.replace(t._createImg('mceItemQuickTime', n), n);
							break;

						case 'audio/x-pn-realaudio-plugin':
							dom.replace(t._createImg('mceItemRealMedia', n), n);
							break;

						default:
							dom.replace(t._createImg('mceItemFlash', n), n);
					}
				}			
			});
		},
                */

                /*
		_createImg : function(cl, n) {
			var im, dom = this.editor.dom, pa = {}, ti = '', args;

			args = ['id', 'name', 'width', 'height', 'bgcolor', 'align', 'flashvars', 'src', 'wmode', 'allowfullscreen', 'quality'];	

			// Create image
			im = dom.create('img', {
				src : this.url + '/img/trans.gif',
				width : dom.getAttrib(n, 'width') || 100,
				height : dom.getAttrib(n, 'height') || 100,
				style : dom.getAttrib(n, 'style'),
				'class' : cl
			});

			// Setup base parameters
			each(args, function(na) {
				var v = dom.getAttrib(n, na);

				if (v)
					pa[na] = v;
			});

			// Add optional parameters
			each(dom.select('span', n), function(n) {
				if (dom.hasClass(n, 'mceItemParam'))
					pa[dom.getAttrib(n, 'name')] = dom.getAttrib(n, '_mce_value');
			});

			// Use src not movie
			if (pa.movie) {
				pa.src = pa.movie;
				delete pa.movie;
			}

			// Merge with embed args
			n = dom.select('.mceItemEmbed', n)[0];
			if (n) {
				each(args, function(na) {
					var v = dom.getAttrib(n, na);

					if (v && !pa[na])
						pa[na] = v;
				});
			}

			delete pa.width;
			delete pa.height;

			im.title = this._serialize(pa);

			return im;
		},
                */

		_parse : function(s) {
			return tinymce.util.JSON.parse('{' + s + '}');
		},

		_serialize : function(o) {
			return tinymce.util.JSON.serialize(o).replace(/[{}]/g, '');
		}
	});

	// Register plugin
	tinymce.PluginManager.add('embedmedia', tinymce.plugins.EmbedMediaPlugin);
})();
