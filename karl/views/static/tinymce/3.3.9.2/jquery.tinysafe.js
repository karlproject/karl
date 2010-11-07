/**
 * jquery.tinysafe.js
 *
 * Copyright 2009, Moxiecode Systems AB
 * Released under LGPL License.
 *
 * License: http://tinymce.moxiecode.com/license
 * Contributing: http://tinymce.moxiecode.com/contributing
 *
 * Copyright 2010, Balazs Ree <ree@greenfinity.hu>
 * Released under LGPL License.
 *
 * Tested with tinymce 3.3.9.2.
 *
 ***************************************************************
 *
 *      "Too much magic is bad for the stomach" 
 *                -- unknown programmer.
 *
 * This is a modified version of jquery.tinymce.js.
 * The original version is monkeypatching various jQuery
 * internals and introduces some features new to
 * jQuery, in order to support better access to the dom 
 * of the tinymce widget from jQuery. They are not
 * needed for tinymce itself to work, which is why this
 * plugin is optional even if one uses the jquery edition
 * of tinymce.
 *
 * Patched internals:
 *
 *     text, html, val, append, prepend, remove, replaceWith,
 *     replaceAll, empty, attr
 *
 * This version is created because some people believe that
 * monkeypatching jQuery is unnecessary, intrusive and 
 * potentially dangerous.
 * Also, without the existance of a full regression test suite
 * we have no guarantee to avoid breaking jQuery or any other
 * code that uses jQuery, in a subtle way.
 *
 * This version makes available all features that the original
 * plugin provides, but in a safe way. No monkeypatch to
 * jQuery is introduced, instead the patched version of
 * an internal X is made available under the name tiny_X.
 *
 *
 * Example
 * -------
 *
 * If you want
 *
 *      $(...).attr('value')
 *
 * to have the capability to return the editor's 
 * current content, you use
 *
 *      $(...).tiny_attr('value')
 *
 * instead. 'tiny_attr' will possess the tinymce magic,
 * while 'attr' will continue to work as everyone
 * in the greater universe excepts it to work.
 *
 * For more examples, and to learn what magic is exactly
 * involved, please refer to the original 
 * documentation of the jquery.tinymce plugin,
 * as-provided by the upstream developers.
 *
 *
 * Usage
 * -----
 *
 * The plugin's name is changed from tinymce to:
 *
 *     $(...).tinysafe({
 *         // options here
 *     });
 *
 * This results in initializing the editor widget on
 * the selected elements.
 *
 * Unlike in the original code, the tiny_X functions
 * are always available, even if tinysafe itself
 * is not called.
 * 
 * The :tinymce pseudo selector is provided without
 * a change from the original version.
 *
 *
 ***************************************************************
 * 
 * Prevent loading javascript and css
 *
 *      aka "Please let me specify what I want to load in my page :)"
 *
 * In some use cases, we want to be able to load all js and css 
 * statically from the html, in order to support concatenated resources,
 * faster pageload, better debuggability. However in this case,
 * tinymce must not load its own resources. By default, this
 * is not supported. This becomes possible with this plugin.
 *
 * The option 'load_js', if set to false, will prevent tinymce
 * from dynamically loading any of its plugin and theme javascript. 
 * This is handy if you have a single concatenated resource
 * which you have already included statically from the html.
 * This would be similar to using a 'compressor' view, but
 * the concatenated script does not need to be called *gzip.js,
 * and it does not actually need to be in the tinymce tree.
 *
 * Preventing dynamic loading of css is also supported. 
 * The option 'load_editor_css', if set to false, will prevent tinymce
 * from dynamically loading any of its ui css. This will
 * ovverride any value of the option 'editor_css'.
 *
 *
 * Notes:
 *
 * - if you do want tinymce to load a single css or a set of css,
 *   leave 'load_editor_css' to true, and specify 'editor_css'
 *   as described in the tinymce documentation.
 *
 * - 'load_editor_css' has no effect to the loading of content
 *   css resources inside the content iframe, which still will 
 *   be loaded by tinymce in each case. If you do want tinymce 
 *   to load a single css or a set of css inside the content 
 *   iframe, use 'content_css' as described in the 
 *   tinymce documentation.
 *
 * - Naturally, if you are setting 'load_js' or 'load_editor_css'
 *   fo false, you become responsible to make sure that
 *   your resources include all necessary theme and plugin
 *   js and css needed by tinymce to work.
 *
 *
 * An example to prevent loading any js and editor css (but still
 * let tinymce load the content css inside the content iframe:
 *
 *     $(...).tinysafe({
 *         // All css and js is loaded statically, in our setup.
 *         load_editor_css: false,
 *         load_js: false,
 *
 *         // url won't be loaded either, but it is
 *         // needed for locating the tinymce tree path.
 *         script_url: 'http://the/real/tinymce',  
 *
 *         // more options here
 *     });
 * 
 *
 *
 *
 *
 ***************************************************************
 */
 
(function($) {
    var undefined,
        lazyLoading,
        delayedInits = [],
        win = window;

    $.fn.tinysafe = function(settings) {
        var self = this, url, ed, base, pos, lang, query = "", suffix = "";

        // No match then just ignore the call
        if (!self.length)
            return self;

        // Get editor instance
        if (!settings)
            return tinyMCE.get(self[0].id);

        function init() {
            var editors = [], initCount = 0;

            // XXX patch is always applied now.
            //if (applyPatch) {
            //    applyPatch();
            //    applyPatch = null;
            //}

            // Create an editor instance for each matched node
            self.each(function(i, node) {
                var ed, id = node.id, oninit = settings.oninit;

                // Generate unique id for target element if needed
                if (!id)
                    node.id = id = tinymce.DOM.uniqueId();

                // Create editor instance and render it
                ed = new tinymce.Editor(id, settings);
                editors.push(ed);

                // Add onInit event listener if the oninit setting is defined
                // this logic will fire the oninit callback ones each
                // matched editor instance is initialized
                if (oninit) {
                    ed.onInit.add(function() {
                        var scope, func = oninit;

                        // Fire the oninit event ones each editor instance is initialized
                        if (++initCount == editors.length) {
                            if (tinymce.is(func, "string")) {
                                scope = (func.indexOf(".") === -1) ? null : tinymce.resolve(func.replace(/\.\w+$/, ""));
                                func = tinymce.resolve(func);
                            }

                            // Call the oninit function with the object
                            func.apply(scope || tinymce, editors);
                        }
                    });
                }
            });

            // Render the editor instances in a separate loop since we
            // need to have the full editors array used in the onInit calls
            $.each(editors, function(i, ed) {
                ed.render();
            });
        }

        // XXX support inhibition of javascript and css loading
        var url = settings.script_url;
        if (settings.load_js === false) {
            if (url.charAt(url.length - 1) != '/') {
                // pad out the directory if needed
                url += '/'; 
            }
            // pretend we are a compressor
            url += 'gzip'; 
        }
        if (settings.load_editor_css === false) {
            // There is no easy way to talk tinymce off
            // from loading the editor_css. Unfortunately, the themes
            // will still load either the editor_css parameter, or
            // preload their own css if editor_css is false.
            // (or do whatever they like, since this is done from
            // the theme's code.)
            // The only sensible trick is to set editor_css to
            // something that we already have: this way no loading
            // will happen, and no 404 either.
            var found;
            $('link').each(function() {
                var link = $(this);
                if (link.attr('rel') == 'stylesheet' && 
                        (! link.attr('type') || link.attr('type') == 'text/css') &&
                        link.attr('href') &&
                        (! link.attr('media') || link.attr('media') == 'screen')) {
                    // use the first good one we find.
                    found = link.attr('href');
                    return false;
                }
            });
            if (! found) {
                // Blast. This should not really happen
                found = 'MISS';
            }
            // set the editor_css
            settings.editor_css = found;
        }

        // Load TinyMCE on demand, if we need to
        if ((settings.load_js === false) ||
           (!win["tinymce"] && !lazyLoading && url)) {
            lazyLoading = 1;
            base = url.substring(0, url.lastIndexOf("/"));

            // Check if it's a dev/src version they want to load then
            // make sure that all plugins, themes etc are loaded in source mode aswell
            if (/_(src|dev)\.js/g.test(url))
                suffix = "_src";

            // Parse out query part, this will be appended to all scripts, css etc to clear browser cache
            pos = url.lastIndexOf("?");
            if (pos != -1)
                query = url.substring(pos + 1);

            // Setup tinyMCEPreInit object this will later be used by the TinyMCE
            // core script to locate other resources like CSS files, dialogs etc
            // You can also predefined a tinyMCEPreInit object and then it will use that instead
            win.tinyMCEPreInit = win.tinyMCEPreInit || {
                base : base,
                suffix : suffix,
                query : query
            };

            // url contains gzip then we assume it's a compressor
            if (url.indexOf('gzip') != -1) {
                lang = settings.language || "en";
                url = url + (/\?/.test(url) ? '&' : '?') + "js=true&core=true&suffix=" + escape(suffix) + "&themes=" + escape(settings.theme) + "&plugins=" + escape(settings.plugins) + "&languages=" + lang;

                // Check if compressor script is already loaded otherwise setup a basic one
                if (!win["tinyMCE_GZ"]) {
                    tinyMCE_GZ = {
                        start : function() {
                            tinymce.suffix = suffix;

                            function load(url) {
                                tinymce.ScriptLoader.markDone(tinyMCE.baseURI.toAbsolute(url));
                            }

                            // Add core languages
                            load("langs/" + lang + ".js");

                            // Add themes with languages
                            load("themes/" + settings.theme + "/editor_template" + suffix + ".js");
                            load("themes/" + settings.theme + "/langs/" + lang + ".js");

                            // Add plugins with languages
                            $.each(settings.plugins.split(","), function(i, name) {
                                if (name) {
                                    load("plugins/" + name + "/editor_plugin" + suffix + ".js");
                                    load("plugins/" + name + "/langs/" + lang + ".js");
                                }
                            });
                        },

                        end : function() {
                        }
                    }
                }
            }

            if (settings.load_js === false) {
                // XXX Set the base url. The tinymce _init
                // is doing this when the script is loaded. Depending on
                // script order, this may be critical.
                // Without this, tinymce won't recognize itself as
                // tinymce, and nothing at all would happen.
                tinymce.baseURL = new tinymce.util.URI(tinymce.documentBaseURL)
                    .toAbsolute(tinyMCEPreInit.base);
                if (tinymce.baseURL.charAt(tinymce.baseURL.length - 1) == '/') {
                    // very important: lack of this leads to double-load and silent errors
                    tinymce.baseURL = tinymce.baseURL.substr(0, tinymce.baseURL.length - 1);
                }
                tinymce.baseURI = new tinymce.util.URI(tinymce.baseURL);
                tinymce.dom.Event.domLoaded = 1;
                // XXX mark all scripts loaded, and init
                tinyMCE_GZ.start();
                // Execute callback after mainscript has been loaded and before the initialization occurs
                if (settings.script_loaded) {
                    settings.script_loaded();
                }
                init();
            }
            // Load the script cached and execute the inits once it's done
            (settings.load_js !== false) && $.ajax({
                type : "GET",
                url : url,
                dataType : "script",
                cache : true,
                success : function() {
                    tinymce.dom.Event.domLoaded = 1;
                    lazyLoading = 2;

                    // Execute callback after mainscript has been loaded and before the initialization occurs
                    if (settings.script_loaded)
                        settings.script_loaded();

                    init();

                    $.each(delayedInits, function(i, init) {
                        init();
                    });
                }
            });
        } else {
            // Delay the init call until tinymce is loaded
            if (lazyLoading === 1)
                delayedInits.push(init);
            else
                init();
        }

        return self;
    };

    // Add :tinymce psuedo selector this will select elements that has been converted into editor instances
    // it's now possible to use things like $('*:tinymce') to get all TinyMCE bound elements.
    $.extend($.expr[":"], {
        tinymce : function(e) {
            return e.id && !!tinyMCE.get(e.id);
        }
    });

    // This function patches internal jQuery functions so that if
    // you for example remove an div element containing an editor it's
    // automatically destroyed by the TinyMCE API
    function applyPatch() {
        // Removes any child editor instances by looking for editor wrapper elements
        function removeEditors(name) {
            // If the function is remove
            if (name === "remove") {
                this.each(function(i, node) {
                    var ed = tinyMCEInstance(node);

                    if (ed)
                        ed.remove();
                });
            }

            this.find("span.mceEditor,div.mceEditor").each(function(i, node) {
                var ed = tinyMCE.get(node.id.replace(/_parent$/, ""));

                if (ed)
                    ed.remove();
            });
        }

        // Loads or saves contents from/to textarea if the value
        // argument is defined it will set the TinyMCE internal contents
        function loadOrSave(value) {
            var self = this, ed;

            // Handle set value
            if (value !== undefined) {
                removeEditors.call(self);

                // Saves the contents before get/set value of textarea/div
                self.each(function(i, node) {
                    var ed;

                    if (ed = tinyMCE.get(node.id))
                        ed.setContent(value);
                });
            } else if (self.length > 0) {
                // Handle get value
                if (ed = tinyMCE.get(self[0].id))
                    return ed.getContent();
            }
        }

        // Returns tinymce instance for the specified element or null if it wasn't found
        function tinyMCEInstance(element) {
            var ed = null;

            (element) && (element.id) && (win["tinymce"]) && (ed = tinyMCE.get(element.id));

            return ed;
        }

        // Checks if the specified set contains tinymce instances
        function containsTinyMCE(matchedSet) {
            return !!((matchedSet) && (matchedSet.length) && (win["tinymce"]) && (matchedSet.is(":tinymce")));
        }

        // Patch various jQuery functions
        var jQueryFn = {};

        // Patch some setter/getter functions these will
        // now be able to set/get the contents of editor instances for
        // example $('#editorid').html('Content'); will update the TinyMCE iframe instance
        $.each(["text", "html", "val"], function(i, name) {
            var origFn = jQueryFn[name] = $.fn[name],
                textProc = (name === "text");

             $.fn['tiny_' + name] = function(value) {
                var self = this;

                if (!containsTinyMCE(self))
                    return origFn.apply(self, arguments);

                if (value !== undefined) {
                    loadOrSave.call(self.filter(":tinymce"), value);
                    origFn.apply(self.not(":tinymce"), arguments);

                    return self; // return original set for chaining
                } else {
                    var ret = "";
                    var args = arguments;
                    
                    (textProc ? self : self.eq(0)).each(function(i, node) {
                        var ed = tinyMCEInstance(node);

                        ret += ed ? (textProc ? ed.getContent().replace(/<(?:"[^"]*"|'[^']*'|[^'">])*>/g, "") : ed.getContent()) : origFn.apply($(node), args);
                    });

                    return ret;
                }
             };
        });

        // Makes it possible to use $('#id').append("content"); to append contents to the TinyMCE editor iframe
        $.each(["append", "prepend"], function(i, name) {
            var origFn = jQueryFn[name] = $.fn[name],
                prepend = (name === "prepend");

             $.fn['tiny_' + name] = function(value) {
                var self = this;

                if (!containsTinyMCE(self))
                    return origFn.apply(self, arguments);

                if (value !== undefined) {
                    self.filter(":tinymce").each(function(i, node) {
                        var ed = tinyMCEInstance(node);

                        ed && ed.setContent(prepend ? value + ed.getContent() : ed.getContent() + value);
                    });

                    origFn.apply(self.not(":tinymce"), arguments);

                    return self; // return original set for chaining
                }
             };
        });

        // Makes sure that the editor instance gets properly destroyed when the parent element is removed
        $.each(["remove", "replaceWith", "replaceAll", "empty"], function(i, name) {
            var origFn = jQueryFn[name] = $.fn[name];

            $.fn['tiny_' + name] = function() {
                removeEditors.call(this, name);

                return origFn.apply(this, arguments);
            };
        });

        jQueryFn.attr = $.fn.attr;

        // Makes sure that $('#tinymce_id').attr('value') gets the editors current HTML contents
        $.fn.tiny_attr = function(name, value, type) {
            var self = this;

            if ((!name) || (name !== "value") || (!containsTinyMCE(self)))
                return jQueryFn.attr.call(self, name, value, type);

            if (value !== undefined) {
                loadOrSave.call(self.filter(":tinymce"), value);
                jQueryFn.attr.call(self.not(":tinymce"), name, value, type);

                return self; // return original set for chaining
            } else {
                var node = self[0], ed = tinyMCEInstance(node);

                return ed ? ed.getContent() : jQueryFn.attr.call($(node), name, value, type);
            }
        };
    }


    // XXX Apply the patch, when the code is loaded.
    if (applyPatch) {
        applyPatch();
        applyPatch = null;
    }

})(jQuery);
