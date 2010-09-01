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
            this._url = url

            ed.onInit.add(function() {
                ed.dom.loadCSS(url + "/css/tinymce.css");
            });
            
            var onBeforeSetContentDelegate = Kaltura.Delegate.create(this, this._onBeforeSetContent);
            ed.onBeforeSetContent.add(onBeforeSetContentDelegate);
            
            var onGetContentDelegate = Kaltura.Delegate.create(this, this._onGetContent);
            ed.onGetContent.add(onGetContentDelegate);
            
             // Register commands
            ed.addCommand('mceKaltura', function() {
                log('button pressed');
            });

            // Register buttons
            ed.addButton('kaltura', {
                title : 'kaltura.kaltura_button_desc',
                image: url+ '/images/interactive_video_button.gif',
                cmd : 'mceKaltura'
            });


        },

        /**
         * Creates control instances based in the incomming name. This method is normally not
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
        },
        
        _tagStart : '[kaltura-widget',
        
        _tagEnd : '/]',
        
        _replaceTagStart : '<img',
        
        _replaceTagEnd : '/>',
        
        _originalHeight: 0,
        
        _originalWidth: 0,
        
        _onBeforeSetContent : function(ed, obj) {
            if (!obj.content)
                return;
                
            var contentData = obj.content;
            var startPos = 0;

            while ((startPos = contentData.indexOf(this._tagStart, startPos)) != -1) {
                var endPos = contentData.indexOf(this._tagEnd, startPos);
                var attribs = this._parseAttributes(contentData.substring(startPos + this._tagStart.length, endPos));
                
                // set defaults if not found
                if (!attribs['wid'])
                    attribs['wid'] = '';
                
                if (!attribs['addpermission'])
                    attribs['addpermission'] = '';
                
                if (!attribs['editpermission'])
                    attribs['editpermission'] = '';
                
                if (!attribs['size'])
                    attribs['size'] = 'custom';

                if (!attribs['align'])
                    attribs['align'] = '';
                
                if (!attribs['width'] || !attribs['height'])
                {
                    attribs['width'] = '410';
                    attribs['height'] = '364';
                }
                
                // for backward compatibility, when we used specific size
                if (attribs['size'] == 'large') 
                {
                    attribs['width'] = '410';
                    attribs['height'] = '364';
                }
                
                if (attribs['size'] == 'small')
                {
                    attribs['width'] = '250';
                    attribs['height'] = '244';
                }
                
                if (attribs['width'] == '410' && attribs['height'] == '364')
                    attribs['size'] = 'large';
                
                if (attribs['width'] == '250' && attribs['height'] == '244')
                    attribs['size'] = 'small';
                
                endPos += this._tagEnd.length;
                var contentDataEnd = contentData.substr(endPos);
                contentData = contentData.substr(0, startPos);

                // build the image tag
                contentData += '<img ';
                contentData += 'src="' + (this._url + '/../thumbnails/placeholder.gif') + '" ';
                contentData += 'title="Kaltura" ';
                contentData += 'alt="Kaltura" ';
                contentData += 'class="';
                    contentData += 'kaltura_item align' + attribs['align'] + ' ';
                    contentData += 'kaltura_add_' + attribs['addpermission'] + ' ';
                    contentData += 'kaltura_edit_' + attribs['editpermission'] + ' ';
                    if (attribs['wid'])
                        contentData += 'kaltura_id_' + attribs['wid'] + ' ';
                    if (attribs['uiconfid'])
                        contentData += 'kaltura_uiconfid_' + attribs['uiconfid'] + ' ';
                    if (attribs['entryid'])
                        contentData += 'kaltura_entryid_' + attribs['entryid'] + ' ';
                contentData += '" '; 
                contentData += 'name="mce_plugin_kaltura_desc" ';
                contentData += 'width="' + attribs['width'] + '" ';
                contentData += 'height="' + attribs['height'] + '" ';
                
                if (attribs['style'])
                    contentData += 'style="' + attribs['style'] + '" ';
                
                contentData += '/>';
                
                contentData += contentDataEnd;
            }
            
            obj.content = contentData;
        },
        
        _onGetContent : function(ed, obj) {
            if (!obj.content)
                return;

            var contentData = obj.content;
            var startPos = 0;
            while ((startPos = contentData.indexOf(this._replaceTagStart, startPos)) != -1) {
                var endPos = contentData.indexOf(this._replaceTagEnd, startPos);
                if (endPos > -1) {
                    var attribs = this._parseAttributes(contentData.substring(startPos + this._replaceTagStart.length, endPos));
                
                    var className = attribs['class'];
                    if (!className || className.indexOf('kaltura_item') == -1) {
                        startPos++;
                        continue;
                    }
                    
                    var wid = "";
                    var addpermission = "";
                    var editpermission = "";
                    var uiconfid = "";
                    var entryid = "";
                    
                    // get the attribs that we saved in the class name
                    var classAttribs = className.split(" "); 
                    for(var j = 0; j < classAttribs.length; j++) {
                        switch (classAttribs[j])
                        {
                            case 'alignright':
                                attribs['align'] = 'right';
                                break;
                            case 'alignleft':
                                attribs['align'] = 'left';
                                break;
                            case 'aligncenter':
                                attribs['align'] = 'center';
                                break;
                            default:
                                classAttrArr = classAttribs[j].match(/kaltura_([a-zA-Z]*)_([\w]*)/);
                                if (classAttrArr && classAttrArr.length == 3) {
                                    switch(classAttrArr[1]) {
                                        case 'id':
                                            if (classAttrArr[2] != "")
                                                wid = classAttrArr[2];
                                            break;
                                        case 'add': 
                                            if (classAttrArr[2] != "")
                                                addpermission = classAttrArr[2];
                                            break;
                                        case 'edit':
                                            if (classAttrArr[2] != "")
                                                editpermission = classAttrArr[2];
                                            break;
                                        case 'uiconfid':
                                            if (classAttrArr[2] != "")
                                                uiconfid = classAttrArr[2];
                                            break;
                                        case 'entryid':
                                            if (classAttrArr[2] != "")
                                                entryid = classAttrArr[2];
                                            break;
                                    }
                                }
                                break;
                        }
                    }
                    
                    endPos += this._replaceTagEnd.length;
                    var contentDataEnd = contentData.substr(endPos);
                    contentData = contentData.substr(0, startPos);
                    

                    contentData += this._tagStart + ' ';
                    if (wid)
                        contentData += 'wid="' + wid + '" ';
                    
                    if (uiconfid)
                        contentData += 'uiconfid="' + uiconfid + '" ';
                    
                    if (entryid)
                        contentData += 'entryid="' + entryid + '" ';
                        
                    contentData += 'width="' + attribs['width'] + '" ';
                    contentData += 'height="' + attribs['height'] + '" ';
                    
                    if (attribs['style'])
                        contentData += 'style="' + attribs['style'] + '" ';
                    
                    contentData += 'addpermission="' +  addpermission + '" ';
                    contentData += 'editpermission="' +  editpermission + '" ';
                    
                    if (attribs['align'])
                        contentData += 'align="' + attribs['align'] + '" '; // align
                    
                    contentData += this._tagEnd;
                    contentData += contentDataEnd;
                }
                else { 
                    startPos++;
                }
            }
            
            obj.content = contentData;
        },
        
        _parseAttributes : function(attribute_string) {
            var attributeName = '';
            var attributeValue = '';
            var withInName;
            var withInValue;
            var attributes = new Array();
            var whiteSpaceRegExp = new RegExp('^[ \n\r\t]+', 'g');
    
            if (attribute_string == null || attribute_string.length < 2)
                return null;
    
            withInName = withInValue = false;
    
            for (var i=0; i<attribute_string.length; i++) {
                var chr = attribute_string.charAt(i);
    
                if ((chr == '"' || chr == "'") && !withInValue)
                    withInValue = true;
                else if ((chr == '"' || chr == "'") && withInValue) {
                    withInValue = false;
    
                    var pos = attributeName.lastIndexOf(' ');
                    if (pos != -1)
                        attributeName = attributeName.substring(pos+1);
    
                    attributes[attributeName.toLowerCase()] = attributeValue.substring(1);
    
                    attributeName = '';
                    attributeValue = '';
                } else if (!whiteSpaceRegExp.test(chr) && !withInName && !withInValue)
                    withInName = true;
    
                if (chr == '=' && withInName)
                    withInName = false;
    
                if (withInName)
                    attributeName += chr;
    
                if (withInValue)
                    attributeValue += chr;
            }
            return attributes;
        }
    });
    
    // Register plugin
    tinymce.PluginManager.add('kaltura', tinymce.plugins.Kaltura);
    tinymce.PluginManager.requireLangPack('kaltura');

})();
