
(function() {

    // unique id needed for the file upload input
    var next_fileinputid = 0;
    // unique id needed to serialize file uploads
    var upload_serial = 0;
    // unique id needed to serialize file uploads
    var external_check_serial = 0;

    // Support classes for the image thumbnail handling
    //
    // Since we may not have $ (jquery) during loading,
    // the initialization will be called later.
    var ImageStripe = function() {
        this.init.apply(this, arguments);
    };
    var register_widgets = function() {
        if ($['tiny']) {
            // widgets registered already
            return;
        }
        $.tiny = {};

        // I was getting desperate to solve this from css,
        // but this iterator seems to be more stable.
        $.fn.tiny_fixIEPanelSize = function(widthdiff, heightdiff) {
            if (!jQuery.boxModel) {
                return this.each(function() {
                    var el = $(this);
                    var w = el.css('width');
                    if (w && w != 'auto') {
                        el.width(parseInt(w) + widthdiff);
                    }
                    var h = el.css('height');
                    if (h && h != 'auto') {
                        el.height(parseInt(h) + heightdiff);
                    }
                });
            }
            return this;
        };

        // the sizes we use all imagedrawer panels:
        // contain 6px padding + 1px border in each direction.
        $.tiny.PANEL_WD = 14;
        $.tiny.PANEL_HD = 14;

        // actually, register the widgets.
        $.widget('tiny.imagedrawerimage', {

            _init: function() {
                // Locate markup
                this.image = this.element.find('.tiny-imagedrawer-image img');
                this.label = this.element.find('.tiny-imagedrawer-imagelabel');
                // Initial value
                if (this.options.record) {
                    this.record(this.options.record);
                }
            },

            record: function(/*optional*/ value) {

                if (typeof value == 'undefined') {
                    // Geting value.
                    return this._record;
                }

                // Seting value.
                //
                // Store the record.
                this._record = value;

                // Show the new values in the widget
                var shortened_title = value.title;
                if (shortened_title && shortened_title.length > 9) {
                    shortened_title = shortened_title.substr(0, 9) + '...';
                }
                this.label.text(shortened_title);
                this.image.attr('src', value.thumbnail_url); 

                // Setting width and height is important for
                // external images, where there is no thumbnail
                // and the fullsize image is used. On IE, the
                // following stanza is needed to get such thumbnails
                // "behave", ie. scale properly
                if (value.thumbnail_width) {
                    this.image.attr('width', value.thumbnail_width); 
                } else {
                    this.image.removeAttr('width');
                }
                if (value.thumbnail_height) {
                    this.image.attr('height', value.thumbnail_height); 
                } else {
                    this.image.removeAttr('height');
                }

                // XXX this will work in jquery.ui >= 1.8
                return this;
            }

        });

        $.extend($.tiny.imagedrawerimage, {
                getter: "record",
                defaults: {
                    record: null
                }
        });


        $.widget('tiny.imagedrawerinfopanel', {

            _init: function() {
                var self = this;
                // Locate markup
                this.info_title = this.element.find('.tiny-imagedrawer-info-title');
                this.info_location = this.element.find('.tiny-imagedrawer-info-location');
                this.info_author = this.element.find('.tiny-imagedrawer-info-author');
                this.info_modified = this.element.find('.tiny-imagedrawer-info-modified');
                this.input_caption = this.element.find('input:checkbox[name=tiny-imagedrawer-input-caption]');
                this.input_captiontext = this.element.find('input:text[name=tiny-imagedrawer-input-captiontext]');
                this.input_align = {};
                this.element.find('input:radio[name=tiny-imagedrawer-input-align]')
                    .each(function(index, value) {
                        self.input_align[$(value).attr('value')] = value;
                    });
                this.input_dimension = this.element.find('select[name=tiny-imagedrawer-input-dimension]');
                this.wrapper_location = this.element.find('.tiny-imagedrawer-info-location-wrapper');
                this.wrapper_author = this.element.find('.tiny-imagedrawer-info-author-wrapper');
                this.wrapper_modified = this.element.find('.tiny-imagedrawer-info-modified-wrapper');
                this.wrapper_captiontext = this.element.find('.tiny-imagedrawer-input-captiontext-wrapper');
                this.buttonset_save = this.element
                    .find('.karl-buttonset.tiny-imagedrawer-buttonset-save')
                    .karlbuttonset({
                        clsContainer: 'tiny-imagedrawer-buttonset-save'
                    });
                this.insert_button = this.buttonset_save
                    .karlbuttonset('getButton', 0);
                this.insert_button_label = this.insert_button
                    .find('a');
                // Wire up the status boxes in the info panel
                this.statusbox = this.element.find('.tiny-imagedrawer-statusbox')
                    .multistatusbox({
                        //clsItem: 'portalMessage',
                        hasCloseButton: false
                    });
                // Wire up the caption selector
                if (this.input_caption.is(':checked')) {
                    this.wrapper_captiontext.show();
                } else {
                    this.wrapper_captiontext.hide();
                }
                this.input_caption.click(function() {
                    if ($(this).is(':checked')) {
                        self.wrapper_captiontext
                            .show('fold')
                            .focus();
                    } else {
                        self.wrapper_captiontext.hide('fold');
                    }
                });
                // Initial value
                if (this.options.insertButtonLabel) {
                    this.insertButtonLabel(this.options.insertButtonLabel);
                }
                if (this.options.record) {
                    this.record(this.options.record);
                }
            },

            insertButtonEnabled: function(/*optional*/ value) {

                if (value === undefined) {
                    // Geting value.
                    this.insert_button.hasClass('ui-state-disabled');
                }

                // Seting value.
                //
                if (value) {
                    this.insert_button.removeClass('ui-state-disabled');
                } else {
                    this.insert_button.addClass('ui-state-disabled');
                }

                // XXX this will work in jquery.ui >= 1.8
                return this;
            },

            insertButtonLabel: function(/*optional*/ value) {

                if (value === undefined) {
                    // Geting value.
                    return this.insert_button_label.text();
                }

                // Seting value.
                //
                this.insert_button_label.attr('title', value);
                this.insert_button_label.text(value);

                // XXX this will work in jquery.ui >= 1.8
                return this;
            },

            record: function(/*optional*/ value) {
                var self = this;

                if (typeof value == 'undefined') {
                    // Geting value.
                    return this._record;
                }

                // Store the record.
                this._record = value;

                // Setting values, taking care of sensible defaults.
                if (value.title) {
                    this.info_title.text(value.title);
                    this.input_captiontext.val(value.title);
                } else {
                    this.info_title.text('No selection');
                    this.input_captiontext.val('');
                }
                var author_name = value.author_name || '';
                this.info_author.text(author_name);
                if (author_name) {
                    this.wrapper_author.show();
                } else {
                    this.wrapper_author.hide();
                }
                var last_modified = value.last_modified || '';
                this.info_modified.text(last_modified);
                if (last_modified) {
                    this.wrapper_modified.show();
                } else {
                    this.wrapper_modified.hide();
                }

                // iterate on the location chain and render it
                this.info_location.html('');
                $(value.location).each(function(i) {
                    if (i > 0) {
                        self.info_location.append(
                            '<span>&nbsp;&gt;&nbsp;</span>'
                        );
                    }
                    self.info_location.append(
                        $('<span></span>')
                            // XXX title should be limited (...)
                            .text(this.title)
                        );
                });
                if (value.location && value.location.length > 0) {
                    this.wrapper_location.show();
                } else {
                    this.wrapper_location.hide();
                }

                // update statuses
                this.statusbox.multistatusbox('clear');
                if (value.error) {
                    this.statusbox.multistatusbox('append', value.error,
                        null, 'ui-state-error ui-corner-all');
                } else if (value.status) {
                    this.statusbox.multistatusbox('append', value.status,
                        null, 'ui-state-highlight ui-corner-all');
                }

                // handle the insert button enabled state
                this.insertButtonEnabled(value.image_url);

                // XXX this will work in jquery.ui >= 1.8
                return this;
            },

            insertOptions: function(/*optional*/ value) {
                var self = this;

                if (typeof value == 'undefined') {
                    // Geting value from the inputs.
                    return {
                        caption: this.input_caption.is(':checked'),
                        captiontext: this.input_captiontext.val(),
                        align: this.element.find('input:radio[name=tiny-imagedrawer-input-align]:checked').val(),
                        dimension: this.input_dimension.val()
                    };
                }

                // Setting values, taking care of sensible defaults.
                if (value) {
                    if (value.caption != undefined) {
                        this.input_caption[0].checked = value.caption;
                        if (value.caption) {
                            this.wrapper_captiontext.show();
                        } else {
                            this.wrapper_captiontext.hide();
                        }
                    }
                    if (value.captiontext != undefined) {
                        this.input_captiontext.val(value.captiontext);
                    }
                    if (value.align != undefined) {
                        this.input_align[value.align].checked = true;
                    }
                    if (value.dimension != undefined) {
                        this.input_dimension.val(value.dimension);
                    }
                }

                // XXX this will work in jquery.ui >= 1.8
                return this;
            }


        });

        $.extend($.tiny.imagedrawerinfopanel, {
                getter: "record insertOptions",
                defaults: {
                    record: null,
                    insertButtonLabel: null
                }
        });



        $.extend(ImageStripe.prototype, {

            init: function(container, column_width, proto_image,
                proto_value) {
                this.container = container;
                this.column_width = column_width;
                this.proto_image = proto_image;
                this.proto_value = proto_value;
                this.reset();
            },

            reset: function() {
                this.offset = 0;
                this.container.empty();
            },

            // Generates a thumb image.
            _thumb: function(/*optional*/ value) {
                return this.proto_image
                    .clone(true)
                    .imagedrawerimage({
                        record: $.extend({}, this.proto_value, value)
                    });
            },

            preload: function(start, end) {
                var self = this;

                var oldstart = this.offset;
                var oldend = oldstart + this.items().length;

                // Check if we are beyond region.
                if ((oldend - oldstart > 0) && 
                        ((end < oldstart) || (start > oldend))) {
                    throw new Error('Preloading non-adjoining regions: must have reset before.');
                }

                var i = start;

                // Prepend records to the container.
                while (i < oldstart) {
                    this._thumb({loading: true}).prependTo(this.container);
                    i += 1;
                }
                // Update the offset
                var decrease_offset = i - start;
                if (decrease_offset > 0) {
                    this.offset -= decrease_offset;
                } else {
                    // No change in offset. At this point we
                    // check if we are after a reset, and initiate
                    // the margin according to the offset.
                    if (this.items().length == 0) {
                        // No previous region.
                        this.offset = start;
                    }
                }

                // Replace records inside the container.
                while (i < Math.min(oldend, end)) {
                    // XXX Just update the value, instead? TODO
                    this._thumb({loading: true}).replaceAll(this.item(i));
                    i += 1;
                }

                // Append records to the container.
                while (i < end) {
                    this._thumb({loading: true}).appendTo(this.container);
                    i += 1;
                }

                this._setLength();
            },

            insertRecord: function(index, /*optional*/ value) {
                // inserts a record at the given position
                // this pushes all following records to the right.

                // Generates the item.
                var newItem = this._thumb(value);

                if (index - this.offset == this.items().length) {
                    // Allow appending the item right at the
                    // end of the stored region.
                    newItem.appendTo(this.container);
                } else {
                    // Insert the item before the given index.
                    var item = this.item(index);
                    // Check if we store this item.
                    if (item.length != 1) {
                        throw new Error('insertRecord must extend a region continously.');
                    }
                    newItem.insertBefore(item);
                }

                this._setLength();

                // Return the newly created object
                return newItem;
            },

            _setLength: function() {
                // set the length of the container to
                // always hold all the elements
                this.container.width(this.items().length 
                    * (this.column_width + 20) + 100);
            },

            moveTo: function(start) {
                this.container.css('margin-left',
                    Math.round((this.offset - start) * this.column_width) 
                    + 'px');
            },

            items: function() {
                // Return all items.
                return this.container.children();
            },

            item: function(index) {
                // Get the item at the given index.
                return this.items().eq(index - this.offset);
            },

            recordAt: function(index, value) {

                var item = this.item(index);
                // Check if we store this item.
                if (item.length != 1) {
                    throw new Error('recordAt with an unstored index: item must have preloaded before.');
                }

                if (typeof value == 'undefined') {
                    // Get the value at the given index.
                    return item.imagedrawerimage('record');
                }

                // Set the value.
                item.imagedrawerimage('record', value);
                
            }

        });
    };


    // allow this to fail if tinymce is not present
    window.tinymce || register_widgets();
    window.tinymce && tinymce.create('tinymce.plugins.ImageDrawerPlugin', {

        // Mandatory parameters:
        //      imagedrawer_dialog_url
        //      imagedrawer_upload_url
        //        -- Only needed if the upload (tab) button is enabled.
        //
        init : function(ed, url) {
            var self = this;
            this.editor = ed;
            this.url = url;

            // Make sure the support classes are loaded...
            // ... we need this because we cannot depend on
            // jquery in the outer closure.
            register_widgets();

            // Mark that we don't have a dialog and that we
            // will need to get it with ajax.
            this.dialog = null;
            // no selection initially
            this.selected_item = undefined; 

            // Register commands
            ed.addCommand('mceImageDrawer', function() {
                // Internal image object like a flash placeholder
                if (ed.dom.getAttrib(ed.selection.getNode(), 'class').indexOf('mceItem') != -1)
                    return;
                
                // Let's see what image the user wants us to replace
                var img = self._getEditorImageSelection();
                if (img) {
                    img = $(img);

                    // Fetch the data from the image
                    self.editor_image_data = self._getEditorImageData(img);

                    // Analyze the source.
                    var re_domain = /^https?:\/\/([^\/\?]*)[\/\?]?/;
                    var a_1 = re_domain.exec(window.location.href);
                    var a_domain = a_1 && a_1[1];
                    var b_1 = re_domain.exec(img.attr('src')); // null if relative
                    var b_domain = b_1 && b_1[1];
                    self.editor_image_data.external = b_1 && a_domain != b_domain;

                } else {
                    // Not replacing (...will insert)
                    self.editor_image_data = null;
                }


                // Do we need a dialog?
                if (! self.dialog) {
                    var data = {};
                    if (self.editor_image_data && ! self.editor_image_data.external) { 
                        // If this is our internal image, we start
                        // on the My Recent tab. The server will
                        // incorporate the image to be replaced
                        // in the thumbnail result list.
                        data = {
                            source: 'myrecent',
                            include_image_url: self.editor_image_data.image_url
                        };
                    }
                    // Make a request to the server to fetch the dialog snippet
                    // as well as the initial batch of the image list
                    $.ajax({
                            type: 'GET',
                            url: ed.getParam('imagedrawer_dialog_url'),
                            data: data,
                            success: function(json) {self._dialogSuccess(json);},
                            error: function(json) {self._dialogError(json);},
                            dataType: 'json'
                        });

                        // XXX show loading status here?
                } else {
                    self._restore_formstate();  // XXX XXX
                    // XXX...
                    var button_value = $(self.buttonset).data('karlbuttonset')
                        .element.children().eq(self.selected_source).attr('value');

                    // Set the Insert/Replace button's text.
                    self._updateInsertReplaceState();
                    // Set the source in case we are replacing.
                    if (self.editor_image_data) {
                        // We are replacing. Source is either My Recent or Web.
                        if (self.editor_image_data.external) {
                            self.buttonset
                                .karlbuttonset('getButton', 3)   // Web
                                .click();
                            self.input_url.val(self.editor_image_data.image_url);
                            self._externalDoCheck({
                                image_url: self.editor_image_data.image_url
                            });
                        } else {
                            if (self.selected_source != 1) {
                                self.buttonset
                                    .karlbuttonset('getButton', 1)   // My Recent
                                    .click();
                            } else if (button_value == 'myrecent' ||
                                       button_value == 'thiscommunity' ) {
                                // need to force the re-fetch
                                self._requestRecords(0, 12, true);   // XXX XXX
                            }
                        } 
                    } else {
                        if (button_value == 'myrecent' ||
                                button_value == 'thiscommunity' ) {
                            // need to force the re-fetch
                            self._requestRecords(0, 12, true);   // XXX XXX
                        }
                    }
                    // We have it, so (re-)open it.
                    self._save_formstate();     // XXX XXX
                    self.dialog.dialog('open');
                    self._restore_formstate();  // XXX XXX
                }

            });

            // Register buttons
            ed.addButton('image', {
                title : 'imagedrawer.image_desc',
                cmd : 'mceImageDrawer'
            });

            // dynamic loading of the plugin's css
            ed.onInit.add(function() {
                if (ed.settings.editor_css !== false) {
                    tinymce.DOM.loadCSS(url + "/css/ui.css");
                }
                //if (ed.settings.content_css !== false) {
                //    ed.dom.loadCSS(url + "/css/content.css");
                //}
            });

        },

        // Hack to work around:
        //   http://sikanrong.com/blog/radio_button_javascript_bug__internet_explorer
        // Every time we open / close the dialog, the snippet will be
        // moved in the dom. Which causes IE to forget the selection of
        // the radio buttons, and revert to their value at creation.
        _save_formstate: function() {
            this._formstate = {
                insertOptions: this.info_panel.imagedrawerinfopanel('insertOptions')
            };
        },
        //
        _restore_formstate: function() {
            this.info_panel.imagedrawerinfopanel('insertOptions',
                    this._formstate.insertOptions);
        },

        _dialogSuccess: function(json) {
            var self = this;
            var ed = this.editor;
            // use error sent by server, if available
            var error = json && json.error;
            if (error) {
                this._dialogError(json);
            }
            //
            // Bring up the dialog
            this.dialog = $(json.dialog_snippet);
            this.dialog.hide().appendTo('body');
            this.dialog.dialog({
                // the next options are adjustable if the style changes
                // Full width is computed from width border and padding.
                // IE's quirkmode is also taken to consideration.
                width: 6 + 390 + 7 + 320 + 6 + (jQuery.boxModel ? 0 : 10), // ?? XXX
                dialogClass: 'tiny-imagedrawer-dialog',
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
            

            //
            // Wire up the dialog
            //
            
            // each tab panel gets selected by a button
            // from the source selection buttonset
            var download_panel = this.dialog.find('.tiny-imagedrawer-panel-download');
            this.upload_panel = this.dialog.find('.tiny-imagedrawer-panel-upload')
                .tiny_fixIEPanelSize($.tiny.PANEL_WD, $.tiny.PANEL_HD); // fix the box model if needed
            this.external_panel = download_panel.find('.tiny-imagedrawer-panel-external')
                .tiny_fixIEPanelSize($.tiny.PANEL_WD, $.tiny.PANEL_HD); // fix the box model if needed
            this.images_panel = this.dialog
                .find('.tiny-imagedrawer-panel-images')
                .tiny_fixIEPanelSize($.tiny.PANEL_WD, $.tiny.PANEL_HD); // fix the box model if needed
            // source selection buttonset
            var top_panel = this.dialog.find('.tiny-imagedrawer-panel-top');
            var source_panel = top_panel.find('.tiny-imagedrawer-sources');
            this.buttonset = this.dialog
                .find('.karl-buttonset.tiny-imagedrawer-buttonset-tabselect');
            this.buttonset
                .karlbuttonset({
                    clsContainer: 'tiny-imagedrawer-buttonset-tabselect'
                })
                .bind('change.karlbuttonset', function(event, button_index, value) {
                    if (value) {
                        // XXX...
                        var button_value = $(this).data('karlbuttonset')
                            .element.children().eq(button_index).attr('value');

                        if (button_value == 'uploadnew') {
                            // Handle the Upload tab
                            self.upload_panel.show();
                            self.images_panel.hide();
                            self.external_panel.hide();
                            // There is only one thumb on the upload panel,
                            // and that should be selected when switched there.
                            var value = self.upload_preview_image
                                .imagedrawerimage('record');
                            if (value && value.image_url) {
                                self._setSelection(self.upload_preview_image);
                            } else {
                                self._setSelection(null);
                            }
                            self.selected_source = button_index;
                        } else if (button_value == 'myrecent' ||
                                   button_value == 'thiscommunity') {
                            // Handle the search result browsers
                            // Did the source change?
                            if (button_index != self.selected_source) {
                                // Yes. Reset the results
                                // and do a new query.
                                self._requestRecords(0, 12, true);   // XXX XXX
                                self.selected_source = button_index;
                                // The selection will resetted, but we
                                // also need to reset the info panel.
                                self.info_panel.imagedrawerinfopanel('record', {});
                            }
                            self.upload_panel.hide();
                            self.images_panel.show();
                            self.external_panel.hide();
                        } else if (button_value == 'external') {
                            // Handle the External tab
                            self.upload_panel.hide();
                            self.images_panel.hide();
                            self.external_panel.show();
                            // There is only one thumb on the external panel,
                            // and that should be selected when switched there.
                            var value = self.external_preview_image
                                .imagedrawerimage('record');
                            if (value && value.image_url) {
                                self._setSelection(self.external_preview_image);
                            } else {
                                self._setSelection(null);
                            }
                            self.selected_source = button_index;
                        }
                    }
                });

            // Wire up the info panel
            this.info_panel = this.dialog.find('.tiny-imagedrawer-panel-info')
                .imagedrawerinfopanel({
                })
                .tiny_fixIEPanelSize($.tiny.PANEL_WD, $.tiny.PANEL_HD); // fix the box model if needed
            // Wire up the Insert / Cancel buttons in the info panel
            this.info_panel.data('imagedrawerinfopanel').buttonset_save
                .bind('change.karlbuttonset', function(event, button_index, value) {
                    if (button_index == 0) { // Insert
                        // If there is no selection, nothing to do.
                        if (self.selected_item == null) {
                            return;
                        }
                        // Insert the selected one to the editor.
                        self._insertToEditor();
                        // Done. Close.
                        self._save_formstate();     // XXX XXX
                        self.dialog.dialog('close');
                        self._restore_formstate();  // XXX XXX
                    } else { // Cancel.
                        self._save_formstate();     // XXX XXX
                        self.dialog.dialog('close');
                        self._restore_formstate();  // XXX XXX
                    }
                });


            // Give the file input field a unique id
            this.fileinputid = 'tiny-imagedrawer-fileinputid-' + next_fileinputid;
            next_fileinputid += 1;
            var fileinput = this.upload_panel.find('.tiny-imagedrawer-fileinput');
            this.textinput = this.upload_panel.find('.tiny-imagedrawer-input-titletext');
            fileinput.attr('id', this.fileinputid);
            // Name is important as well!
            if (! fileinput.attr('name')) {
                // Give it default 'file', if it is not specified.
                // (Note, It will become the parameter name of the file
                // in the post.)
                fileinput.attr('name', 'file');
            }
            this._fileinput_change = function() {
                // If the file is selected, fill out the title.
                var value = '' + this.value;
                // XXX We want only the basename of the file. However
                // on Windows we get the full path. To make sure
                // we don't get the full path, we calculate the
                // basename ourselves.
                var index = Math.max(value.lastIndexOf('/'), value.lastIndexOf('\\'));
                if (index != -1) {
                    value = value.substring(index + 1);
                }
                self.textinput.val(value);
                // reset the buttonset state
                // so, upload becomes clickable.
                self._uploadReset();
                self.buttonset_upload
                    .karlbuttonset('getButton', 0).removeClass('ui-state-disabled');
                self.buttonset_upload
                    .karlbuttonset('getButton', 1).addClass('ui-state-disabled');
            };
            fileinput.change(this._fileinput_change);

            // Upload panel
            this.upload_statusbox = this.upload_panel.find('.tiny-imagedrawer-statusbox')
                .multistatusbox({
                    //clsItem: 'portalMessage',
                    hasCloseButton: false
                });
            // Wire up the Upload button
            this.buttonset_upload = this.upload_panel
                .find('.karl-buttonset.tiny-imagedrawer-buttonset-upload')
                .karlbuttonset({
                    clsContainer: 'tiny-imagedrawer-buttonset-upload'
                })
                .bind('change.karlbuttonset', function(event, button_index, value) {
                    var buttonset = $(this);
                    if (button_index == 0) { // upload
                        // Signal the start of this upload
                        var eventContext = {};
                        upload_serial += 1;
                        eventContext.upload_serial = upload_serial;
                        self._uploadStart(eventContext);
                        // enable the reset button
                        buttonset.karlbuttonset('getButton', 0).addClass('ui-state-disabled');
                        buttonset.karlbuttonset('getButton', 1).removeClass('ui-state-disabled');

                        // Initiate the upload
                        $.ajaxFileUpload({
                            url: ed.getParam('imagedrawer_upload_url'),
                            secureuri: false,
                            fileElementId: self.fileinputid,
                            extraParams: {
                                // extra parameters passed with the upload
                                title: self.textinput.val()
                            },
                            dataType: 'json',
                            success: function(json, status) {
                                self._uploadSuccess(json, eventContext);
                            },
                            error: function (json, status, e) {
                                // Consider using the exception's text,
                                // if available. This shows us a sensible message
                                // about client side errors, including the 404
                                // which results in eval-error.
                                if (e && e.message) {
                                    json = {error: e.message};
                                }
                                self._uploadError(json, eventContext);
                            }
                        });

                    } else { // Reset in-progress upload
                        // by increasing the serial
                        // we ignore the current upload's result
                        upload_serial += 1;
                        // Ignore what is going on
                        self._uploadReset();
                        // reset the buttonset state
                        buttonset.karlbuttonset('getButton', 0).removeClass('ui-state-disabled');
                        buttonset.karlbuttonset('getButton', 1).addClass('ui-state-disabled');
                    }
                });


            // Web (was: external) panel
            this.input_url = this.external_panel.find('.tiny-imagedrawer-input-url');
            this.label_previewtext = this.external_panel.find('.tiny-imagedrawer-external-previewtext');
            this.external_statusbox = this.external_panel.find('.tiny-imagedrawer-statusbox')
                .multistatusbox({
                    //clsItem: 'portalMessage',
                    hasCloseButton: false
                });
            // Wire up the Check button
            this.buttonset_check = this.external_panel
                .find('.karl-buttonset.tiny-imagedrawer-buttonset-check')
                .karlbuttonset({
                    clsContainer: 'tiny-imagedrawer-buttonset-check'
                })
                .bind('change.karlbuttonset', function(event, button_index, value) {
                    var buttonset = $(this);
                    //if (button_index == 0) { // check                    
                        self._externalDoCheck({
                            image_url: self.input_url.val()
                        });
                    // }
                });

            // Wire the image list
            // 
            // First, it contains a single image. We save
            // this as hidden, and will use it
            // to clone any images.
            this.proto_image = this.images_panel
                .find('ul.tiny-imagedrawer-imagestripe > li')
                .eq(0);
            var proto_wrapper = $('<ul></ul>')
                .hide()
                .appendTo(this.images_panel)
                .append(this.proto_image);
            // Wire the proto image completely.
            this.proto_image
                .dblclick(function(event) {
                    // Doubleclick on the images acts the same as 
                    // pressing the insert button. 
                    //
                    //
                    var value = $(this).imagedrawerimage('record');
                    // Only act if it contains an insertable image!
                    if (value && value.image_url) {
                        // Insert the selected one to the editor.
                        self._insertToEditor(this);
                        // And close the dialog.
                        self._save_formstate();     // XXX XXX
                        self.dialog.dialog('close');
                        self._restore_formstate();  // XXX XXX
                    }
                    // Default clicks should be prevented.
                    event.preventDefault();
                })
                .click(function(event) {
                    // Clicking on an image selects it.
                    self._setSelection(this);
                    event.preventDefault();
                })
                .hover(
                    function() { $(this).addClass('ui-state-hover'); },
                    function() { $(this).removeClass('ui-state-hover'); }
                );

            // In case there are any other image prototypes:
            // we get rid of them.
            this.images_panel
                .find('ul.tiny-imagedrawer-imagestripe > li')
                .remove();

            // column size is the same in all stripes 
            this.visible_columns = 4;

            // We have the following stripes to take care of:
            // - 3 in the download panel
            // - 1 in the upload panel
            // - 1 in the external panel
            
            // handle the stripes in the download panel
            this.stripes = [];
            this.images_panel.find('ul.tiny-imagedrawer-imagestripe')
                .each(function(index) {
                    self.stripes.push(
                        new ImageStripe($(this), 95, self.proto_image, {
                            title: self.editor.getLang('imagedrawer.loading_title'),
                            thumbnail_url: self.url + '/images/default_image.png'
                        })
                    );
                });
            // A counter to enable rejection of obsolate batches
            this.region_id = 0;
            // Wire the scrollbar in the download panel
            this.scrollbar = this.images_panel.find('.tiny-imagedrawer-scrollbar')
                .karlslider({
                    enableClickJump: true,
                    enableKeyJump: true,
                    slide: function(e, ui) {
                        self._moveStripe(ui.value / 100);
                    }
                });

            // handle the image in the upload panel
            this.upload_preview_image = this.proto_image.clone(true)
                .imagedrawerimage({});
            this.upload_panel.find('.tiny-imagedrawer-image')
                .replaceWith(this.upload_preview_image);
            // reset the upload state
            this._uploadReset();

            // handle the image in the external panel
            this.external_preview_image = this.proto_image.clone(true)
                .imagedrawerimage({});
            this.external_panel.find('.tiny-imagedrawer-image')
                .replaceWith(this.external_preview_image);
            // reset the external check state
            this._externalReset();

            // Wire up the help panel
            var help_panel = this.dialog.find('.tiny-imagedrawer-panel-help')
                .hide();
            var help_panel_state_shown = false;
            help_panel.find('.karl-buttonset')
                .karlbuttonset({
                    clsContainer: 'tiny-imagedrawer-buttonset-cancelhelp'
                })
                .bind('change.karlbuttonset', function(event, button_index, value) {
                    help_panel.hide('slow');
                    download_panel.show('slow');
                    source_panel.show('slow');
                    help_panel_state_shown = false;
                });
            this.dialog.find('.tiny-imagedrawer-button-help')
                .click(function(event) {
                    if (! help_panel_state_shown) {
                        help_panel.show('fold');
                        source_panel.hide();
                        download_panel.hide();
                        help_panel_state_shown = true;
                    }
                    event.preventDefault();
                });


            // Check that the slider is either jquery ui version 1.8,
            // or that the code is patched with 1.7.
            // The bug in question would prevent the slider to ever go
            // back to value 0.
            if ($.ui.version < '1.8' && ! this.scrollbar.data('karlslider')._uiHash_patched) {
                throw new Error('jquery-ui version >= 1.8, or patched 1.7 version required.');
            }

            // Set the Insert/Replace button's text,
            // as well as the title on the top.
            this.title_tag = this.dialog
                .find('.tiny-imagedrawer-title');
            self._updateInsertReplaceState();

            //
            // Render the first batch of images
            //
            if (json.images_info) {
                this._initImages(json.images_info);
                this._loadRecords(json.images_info);
            }

            // force initial selection to null 
            self._setSelection(null);


            // Initial source tab switch
            if (this.editor_image_data) {
                // We are replacing. Source is either My Recent or Web.
                if (this.editor_image_data.external) {
                    this.buttonset
                        .karlbuttonset('getButton', 3)   // Web
                        .click();
                    this.input_url.val(this.editor_image_data.image_url);
                    this._externalDoCheck({
                        image_url: this.editor_image_data.image_url
                    });
                } else {
                    this.selected_source = 1;    // My Recent
                    // this will change the tabbing but importantly
                    // _not_ re-fetch the data set
                    this.buttonset
                        .karlbuttonset('getButton', 1)   // My Recent
                        .click();
                    // We select the
                    // first element. XXX Note in a refined implementation,
                    // the server should not append the replaced image as
                    // a first fake, but return the (source tab / ) batch
                    // that contains the image, so the client could just
                    // select it whichever index it has.
                    this._setSelection(this._getListItem(0));
                    // prevent selection for another time
                    this.editor_image_data._selected_once = true;
                }
            } else {
                // We are inserting (not replacing).
                // panels are shown based on initial selection
                this.selected_source = this.buttonset[0].selectedIndex; 
                // (Note: we use the index, not the option values,
                // which are irrelevant for the working of this code.)
            }

            // XXX...
            var button_value = this.buttonset.data('karlbuttonset')
                .element.children().eq(this.selected_source).attr('value');

            if (button_value == 'uploadnew') {
                this.upload_panel.show();
                this.images_panel.hide();
                this.external_panel.hide();
            } else if (button_value == 'myrecent' ||
                       button_value == 'thiscommunity') {
                this.upload_panel.hide();
                this.images_panel.show();
                this.external_panel.hide();
            } else if (button_value == 'external') {
                this.upload_panel.hide();
                this.images_panel.hide();
                this.external_panel.show();
            }

            // Finally, open the dialog.
            this._save_formstate();     // XXX XXX
            this.dialog.dialog('open');
            this._restore_formstate();  // XXX XXX
        },
            
        // Initialize images for the given search criteria.
        _initImages: function(images_info) {
            // Reset the region control
            this.region_start = 0;
            this.region_end = images_info.records.length;
            this.region_total = images_info.totalRecords;
            this._resetStripe();
            // Preload the region
            this._preloadRegion(this.region_start, this.region_end);
            this._moveStripe(this.scrollbar.karlslider('value') / 100);
            // Set the jump increment of the slider.
            // One jump step should scroll ahead one full page.
            var jumpStep = Math.floor(100 / (Math.ceil(this.region_total / this.stripes.length)
                    ) * this.visible_columns); 
            this.scrollbar.karlslider('option', 'jumpStep', jumpStep);
        },

        _dialogError: function(json) {
            // use error sent by server, if available
            var error = json && json.error;
            if (! error) {
                error = 'Server error when fetching drawer_dialog_view.html';
            }
            // XXX XXX XXX do something...
            alert(error);
        },

        _dataSuccess: function(json, region_id, initial) {

            var self = this;
            // use error sent by server, if available
            var error = json && json.error;
            if (error) {
                this._dataError(json);
            }

            if (this.region_id != region_id) {
                // Wrong region. Discard.
                // (This was a region we asked for
                // before a previous reset, but
                // arrived later.)
                ////console.log('Discarding', json.images_info.start, 
                ////    json.images_info.start + json.images_info.records.length);
                return;
            }
            
            // if this is an initial batch: set up the size
            if (initial) {
               this._initImages(json.images_info); 
            }

            // load the records 
            this._loadRecords(json.images_info);

            // If we are in the initial batch: we select the
            // first element. XXX Note in a refined implementation,
            // the server should not append the replaced image as
            // a first fake, but return the (source tab / ) batch
            // that contains the image, so the client could just
            // select it whichever index it has.
            if (initial && this.editor_image_data
                    && ! this.editor_image_data.external
                    && ! this.editor_image_data._selected_once) {
                // XXX ... maybe, assert that we loaded record 0?
                // Select the first element
                this._setSelection(this._getListItem(0));
                // prevent selection for another time
                this.editor_image_data._selected_once = true;
            }

        },

        _dataError: function(json) {
            // use error sent by server, if available
            var error = json && json.error;
            if (! error) {
                error = 'Server error when fetching drawer_data_view.html';
            }
            // XXX XXX XXX do something...
            alert(error);
        },

        _uploadStart: function(eventContext) {
            // Start the throbber
            this.upload_preview_image
                .parent().show();
            this.upload_preview_image
                .imagedrawerimage('record', 
                {
                    loading: true,
                    title: this.textinput.val(),
                    thumbnail_url: this.url + '/images/throbber.gif'
                });
            // clear the status box
            this.upload_statusbox.multistatusbox('clear');
        },

        _uploadReset: function() {
            // hide the image
            this.upload_preview_image
                .parent().hide();
            this.upload_preview_image
                .imagedrawerimage('record', 
                {
                    loading: true,
                    thumbnail_url: this.url + '/images/throbber.gif'
                });
            // clear the status box
            this.upload_statusbox.multistatusbox('clear');
            // clear the selection
            this._setSelection(null);
        },

        _uploadSuccess: function(json, eventContext) {
            var self = this;
            // use error sent by server, if available
            var error = json && json.error;
            if (error) {
                this._uploadError(json, eventContext);
                return;
            }

            // prevent doing anything if this is not the current upload
            if (eventContext.upload_serial != upload_serial) {
                return;
            }

            // Update the image data that just arrived
            this.upload_preview_image
                .imagedrawerimage('record', json.upload_image_info);
            //
            // If we are still on
            // the upload tab: select it,
            if (this.buttonset.val() == 'uploadnew') {
                if (this.selected_item == null) {
                    this._setSelection(this.upload_preview_image);
                } else {
                    // This is the selected item. Update the info panel.
                    this._updateInfoPanel();
                }
            }
        },

        _uploadError: function(json, eventContext) {

            // prevent doing anything if this is not the current upload
            if (eventContext.upload_serial != upload_serial) {
                return;
            }

            // use error sent by server, if available
            var error = json && json.error;
            if (! error) {
                error = 'Server error when fetching drawer_upload_view.html';
            }
            // hide the image, and
            // Get the existing data record and save the error in it.
            this.upload_preview_image
                .parent().hide();
            this.upload_preview_image
                .imagedrawerimage('record', 
                $.extend(this.upload_preview_image.imagedrawerimage('record'),
                    {
                        //thumbnail_url: this.url + '/images/error.png'
                        thumbnail_url: this.url + '/images/throbber.gif'
                    }
                )
            );
            // Show the error in the message box
            this.upload_statusbox.multistatusbox('clearAndAppend', error,
                        null, 'ui-state-error ui-corner-all');
            // update selection
            if (this.buttonset.val() == 'uploadnew') {
                // We are the selected item. Update the info panel.
                this._updateInfoPanel();
            }
        },

        _externalDoCheck: function(eventContext) {
            var self = this;

            external_check_serial += 1;
            eventContext.external_check_serial = external_check_serial;
            this._externalStart(eventContext);

            // Initiate the check
            var img = new Image();

            $(img)
                .load(function() {
                    self._externalSuccess(this, eventContext);
                })
                .error(function() {
                    self._externalError(this, eventContext);
                })
                // XXX It is _very_ important to have this _after_
                // setting the load handler, to satisfy IE. 
                // Explanation: If the image
                // is cached, IE will _never_ execute the onload
                // handler if the src is set preceding the handler
                // setup. This is pretty unexpected, concerning
                // that javascript should execute single-threaded.
                .attr('src', eventContext.image_url);
        },

        _externalStart: function(eventContext) {
            var image_url = eventContext.image_url;
            // XXX TODO eventually, title could be calculated
            // XXX from the image_url.
            var title = 'External image';

            // Start the throbber
            this.external_preview_image
                .parent().show();
            this.external_preview_image
                .imagedrawerimage('record', {
                    loading: true,
                    title: title,
                    thumbnail_url: this.url + '/images/throbber.gif',
                    location: [{
                        title: image_url,
                        href: image_url
                        }]
                });

            // clear the status box
            this.external_statusbox.multistatusbox('clear');
            // hide the "none selected" label
            this.label_previewtext.hide(); 
        },

        _externalReset: function() {
            // hide the image
            this.external_preview_image
                .parent().hide();
            this.external_preview_image
                .imagedrawerimage('record', 
                {
                    loading: true,
                    thumbnail_url: this.url + '/images/throbber.gif'
                });
            // clear the status box
            this.external_statusbox.multistatusbox('clear');
            // clear the selection
            this._setSelection(null);
            // show the "none selected" label
            this.label_previewtext.show(); 
        },

        _externalSuccess: function(img, eventContext) {
            var self = this;

            // prevent doing anything if this is not the current upload
            if (eventContext.external_check_serial != external_check_serial) {
                return;
            }

            // We will not actually use a thumbnail image, because
            // for external images, this is not available. We will
            // use the original size image. This works everywhere
            // but on IE. For the sole purpose of making this
            // work on IE, we must calculate and explicitely set
            // the size of the thumbnails.
            var thumbnail_width = undefined;
            var thumbnail_height = undefined;

            // We _could_ have it everywhere, but apart from IE
            // it makes no point, and it makes the image appearing
            // ugly (size set, before the image actually gets loaded)
            if ($.browser.msie) {
                var clipping_size = 175;   // 175px: must match the css
                if (img.width > clipping_size || img.height > clipping_size) {
                    var ratio = img.width / img.height;
                    if (ratio > 1) {
                        thumbnail_width = clipping_size;
                        thumbnail_height = Math.floor(clipping_size / ratio);
                    } else {
                        thumbnail_width = Math.floor(clipping_size * ratio);
                        thumbnail_height = clipping_size;
                    }
                }
            }

            // update the record with the image sizes we have now
            // and also set the thumbnail to show the image
            this.external_preview_image.imagedrawerimage('record', $.extend({},
                this.external_preview_image.imagedrawerimage('record'), {
                    image_width: img.width,
                    image_height: img.height,
                    image_url: eventContext.image_url,
                    thumbnail_url: eventContext.image_url,
                    thumbnail_width: thumbnail_width,
                    thumbnail_height: thumbnail_height
            }));

            // clear the status box
            this.external_statusbox.multistatusbox('clear');
            // hide the "none selected" label
            this.label_previewtext.hide(); 
            // If we are still on
            // the external tab: select it,
            if (this.buttonset.val() == 'external') {
                if (this.selected_item == null) {
                    this._setSelection(this.external_preview_image);
                } else {
                    // This is the selected item. Update the info panel.
                    this._updateInfoPanel();
                }
            }
        },

        _externalError: function(img, eventContext) {
            // prevent doing anything if this is not the current check
            if (eventContext.external_check_serial != external_check_serial) {
                return;
            }

            var error = 'Wrong url, or not an image.';

            // hide the image, and
            // Get the existing data record and save the error in it.
            this.external_preview_image
                .parent().hide();
            this.external_preview_image
                .imagedrawerimage('record', 
                $.extend(this.upload_preview_image.imagedrawerimage('record'),
                    {
                        //thumbnail_url: this.url + '/images/error.png'
                        thumbnail_url: this.url + '/images/throbber.gif'
                    }
                )
            );
            // Show the error in the message box
            this.external_statusbox.multistatusbox('clearAndAppend', error,
                        null, 'ui-state-error ui-corner-all');
            // show the "none selected" label
            this.label_previewtext.show(); 
            // update selection
            if (this.buttonset.val() == 'external') {
                // We are the selected item. Update the info panel.
                this._updateInfoPanel();
            }
        },

        _getListItem: function(index) {
            var stripenum = this.stripes.length;
            var whichstripe = index % stripenum;
            return this.stripes[whichstripe]
                    .item(Math.floor((index + whichstripe) / stripenum));
        },

        _setSelection: function(item) {

            if (item) {
                item = $(item);
            }

            if ((this.selected_item && this.selected_item[0]) === 
                    (item && item[0])) {
                // no change in selection. Nothing to do
                return
            }

            if (this.selected_item != null) {
                // unselect previous one
                this.selected_item.removeClass('ui-state-default ui-state-active');
            }

            this.selected_item = item;
            this._updateInfoPanel();
        },

        _updateInfoPanel: function() {
            var item = this.selected_item;
            if (item != null) {
                // select new one
                // (Use active rather than highlight.)
                item.addClass('ui-state-default ui-state-active');
                var record = item.imagedrawerimage('record');
                this.info_panel.imagedrawerinfopanel('record', record);
            } else {
                this.info_panel.imagedrawerinfopanel('record', {});
            }
        },

        _preloadRegion: function(start, end) {
            // Preload. This will create a "loading" image.
            var stripenum = this.stripes.length;
            $(this.stripes).each(function(index) {
                var revindex = stripenum - index - 1;
                this.preload(
                    Math.floor((start + revindex) / stripenum),
                    Math.floor((end + revindex) / stripenum)
                );
            });
        },

        _resetStripe: function() {
            $(this.stripes).each(function(index) {
                this.reset();
            });
            // increase region counter
            this.region_id += 1;
            // reset the selection
            this._setSelection(null);
            // reset the scrollbar
            this.scrollbar.karlslider('value', 0);
        },

        _moveStripe: function(percentage_float) {
            // Move the stripe to a percentage position.
            // Load records as needed.
            //
            var self = this;

            var slider_index = percentage_float * 
                    (Math.ceil(this.region_total / this.stripes.length)
                    - this.visible_columns); 
            
            if (slider_index < 0) {
                // Region fits entirely without scrolling.
                // Do nothing.
                return;
            }

            // See which region is needed
            var visible_start = Math.floor(slider_index * this.stripes.length);
            var visible_end = Math.ceil(slider_index + this.visible_columns) 
                                    * this.stripes.length;
            var needed_start;
            var needed_end;
            var needed_total;
            if ((visible_start < this.region_start) || 
                    (visible_end > this.region_end)) {
                // We need to acquire this region.
                var minimal_batch = 12;
                if (visible_start < this.region_start) {
                    // prepending
                    needed_end = visible_end;
                    // Is it non-overlapping?
                    if (needed_end < this.region_start) {
                        // Reset everything. We need to start
                        // a new region.
                        ////console.log('Resetting <');
                        this._resetStripe();
                        this.region_end = needed_end;
                    } else {
                        needed_end = this.region_start;
                    }
                    needed_start = Math.min(visible_start,
                            needed_end - minimal_batch);
                    needed_start = Math.max(needed_start, 0);
                    this.region_start = needed_start;
                } else if (visible_end > this.region_end) {
                    // appending
                    needed_start = visible_start;
                    // Is it non-overlapping?
                    if (needed_start > this.region_end) {
                        // Reset everything. We need to start
                        // a new region.
                        ////console.log('Resetting >');
                        this._resetStripe();
                        this.region_start = needed_start;
                    } else {
                        needed_start = this.region_end;
                    }
                    // Assure minimal batching
                    needed_end = Math.max(visible_end,
                        needed_start + minimal_batch);
                    needed_end = Math.min(needed_end, this.region_total);
                    this.region_end = needed_end;
                }
                
                if (needed_start < needed_end) {
                    ////console.log('Preloading', needed_start, needed_end);
                    this._preloadRegion(needed_start, needed_end);
                    var region_id = this.region_id;
                    // load the required data
                    this._requestRecords(needed_start, needed_end - needed_start, false);
                }

            }

            // Move to the position
            $(this.stripes).each(function(index) {
                this.moveTo(slider_index);
            });

        },

        _requestRecords: function(start, limit, /*optional*/ initial) {
            // XXX There are two invariants that this method
            // fetches from the dom:
            // - the source parameter (fetched from the buttonset)
            // - the url of the replaced (internal) image
            var self = this;
            // load the required data
            var region_id = this.region_id;
            var data = {
                start: start, 
                limit: limit,
                sort_on: 'creation_date',
                reverse: '1',
                source: this.buttonset.val()
            };
            // if replacing, we pass the image_url of the image
            // that we want to include into the result set
            // Simple implementation on server side may present
            // this image as first in the My Recent tab.
            if (this.editor_image_data && ! this.editor_image_data.external) {
                data.include_image_url = this.editor_image_data.image_url;
            }
            $.ajax({
                type: 'GET',
                url: this.editor.getParam('imagedrawer_data_url'),
                data: data,
                success: function(json) { self._dataSuccess(json, region_id, initial); },
                error: function(json) { self._dataError(json); },
                dataType: 'json'
            });
        },

        _loadRecords: function(images_info) {
            var self = this;
            var start = images_info.start;
            // Append these records
            var stripenum = this.stripes.length;
            $.each(images_info.records, function(index) {
                var whichstripe = (index + start) % stripenum;
                self.stripes[whichstripe].recordAt(
                        Math.floor((index + start) / stripenum),
                        this);
            });
        },

        _insertToEditor: function(/*optional*/ item) {
    
            var record;
            if (item) {
                // allow to shortcut insert a given image item
                record = $(item).imagedrawerimage('record');
            } else {
                // normally, we're inserting what shows in the info panel
                record = this.info_panel.imagedrawerinfopanel('record');
            }

            var ed = this.editor;
            var v;
            var el;

            // get the insertion options from the info panel
            var insertOptions = this.info_panel.imagedrawerinfopanel('insertOptions');

            // In principle, we use the real image size
            // for the insertion,
            // but we do want to limit width and height
            // initially to a sensible max.
            var width = record.image_width;
            var height = record.image_height;
            var max_width;
            var max_height;
            var dim = {
                original: {max_width: 530, max_height: 530},
                large: {max_width: 400, max_height: 400},
                medium: {max_width: 250, max_height: 250},
                small: {max_width: 100, max_height: 100}
            }[insertOptions.dimension];
            var max_width = dim.max_width;
            var max_height = dim.max_height;
            if (width > max_width) {
                height = Math.floor(height * max_width / width);
                width = max_width;
            }
            if (height > max_height) {
                width = Math.floor(width * max_height / height);
                height = max_height;
            }

            var klass = '';

            // Set the caption
            alt = insertOptions.captiontext;
            if (insertOptions.caption) {
                klass = (klass ? klass + ' ' : '') + 'tiny-imagedrawer-captioned';
            }
            // set the align
            var style = '';
            var align;
            if (insertOptions.align == 'left') {
                align = 'left';
            } else if (insertOptions.align == 'right') {
                align = 'right';
            } else if (insertOptions.align == 'center') {
                style = 'display: block; margin-left: auto; margin-right: auto; text-align: center;';
                align = null;
            }

            //
            var args = {
                src: record.image_url,
                align: align,
                width: width,
                height: height,
                alt: alt,
                'class': klass,
                style: style

                // constrain (bool)
                // vspace
                // hspace
                // border
                // title
                // class
                // onmousemovecheck (bool)
                // onmouseoversrc
                // onmouseoutsrc
                // out-list
                // id
                // dir (ltr, rtl)
                // lang
                // usemap
                // longdesc
            }

            // XXX ???
            //if (ed.settings.inline_styles) {
            //    // Remove deprecated values
            //    args.vspace = '';
            //    args.hspace = '';
            //    args.border = '';
            //    args.align = '';
            //}

            // Fixes crash in Safari
            if (tinymce.isWebKit)
                ed.getWin().focus();

            args.onmouseover = args.onmouseout = '';

            if (args.onmousemovecheck) {
                if (args.onmouseoversrc) {
                    args.onmouseover = "this.src='" + args.onmouseoversrc + "';";
                }

                if (args.onmouseoutsrc)
                    args.onmouseout = "this.src='" + args.onmouseoutsrc + "';";
            }

            // Insert / Replace image.
            var editorImage = this._getEditorImageSelection();
            if (editorImage) {
                // We are replacing the image.
                ed.dom.setAttribs(editorImage, args);
                // Needed.
                ed.execCommand('mceRepaint');
            } else {
                // We are inserting a new image.
                ed.execCommand('mceInsertContent', false, '<img id="__mce_tmp" />', {skip_undo : 1});
                ed.dom.setAttribs('__mce_tmp', args);
                ed.dom.setAttrib('__mce_tmp', 'id', '');
                ed.undoManager.add();
            }


        },

        // Either return the selected image in the editor,
        // or null, in case we are inserting.
        _getEditorImageSelection: function() {

            var ed = this.editor;
            var el = ed.selection.getNode();

            // XXX Workaround for weird issue. Insert an image right when the editor
            // comes up. Select the image and try to upload a different one in place
            // of it. In the first case this fails; upon reselecting the image again,
            // the problem goes away. It seems that if an image is inserted, under
            // certain conditions, a new
            // paragraph is wrapped around it, and upon selecting the image, the
            // <p> wrapper will appear in the selection, which would make
            // the insertion fail.
            //
            // Tests need to include:
            // - selecting an image in an empty P (should replace!!)
            // - selecting an image with a P with spaces after it
            // - selecting a space in the same P where the image is (should insert)
            //
            if (el && el.nodeName == 'P') {
                var nicetry = el.childNodes[ed.selection.getRng().startOffset];
                if (nicetry && nicetry.nodeName == 'IMG') {
                    // Use this for the selection, eh...
                    el = nicetry;
                }
            }
            // XXX End of workaround. Note this should be tested with selenium.
            
            if (el && el.nodeName == 'IMG') {
                return el;
            } else {
                // No image selection. Will insert a new image.
                return null;
            }
        },

        _getEditorImageData: function(img) {
            img = $(img);
            // Figure properties of the image
            var w = img.attr('width');
            var h = img.attr('height');
            var d = {
                insert_width:   w, //img.attr('width'),
                insert_height:  h, //img.attr('height'),
                caption:        img.hasClass('tiny-imagedrawer-captioned'),
                captiontext:    img.attr('alt'),
                image_url:      img.attr('src'),
                dimension: 'original'
            };
            $.each([['small', 100], ['medium', 250], ['large', 400]],
                function(index, value) {
                    if (w <= value[1] && h <= value[1]) {
                        d.dimension = value[0];
                        return false;   // break
                    }
                }
            );
            if (img.css('float') == 'left') {
                d.align = 'left';
            } else if (img.css('float') == 'right') {
                d.align = 'right';
            } else if (img.css('margin-left') == 'auto' && 
                       img.css('margin-right') == 'auto') {
                d.align = 'center';
            } else {
                // no hint on align.
                d.align = null;
            }
            return d;
        },

        _updateInsertReplaceState: function() {
            var self = this;
            var title;
            var button_label;
            var d = this.editor_image_data;

            if (d) {
                title = 'Replace Image';
                button_label = 'Replace';
                // Set the insertion options in the info panel
                this.info_panel.imagedrawerinfopanel('insertOptions', d);
            } else {
                title = 'Insert Image';
                button_label = 'Insert';
            }
            // update the button
            this.info_panel.imagedrawerinfopanel('insertButtonLabel', button_label);
            // update the main title on the top
            this.title_tag.text(title);

        },

        getInfo : function() {
            return {
                longname : 'Image Drawer',
                author : 'Thomas Moroz, Open Society Institute',
                authorurl : '',
                infourl : '',
                version : '1.0'
            };
        }
    });

    // Register plugin
    // allow this to fail if tinymce is not present
    if (window.tinymce) {
        tinymce.PluginManager.add('imagedrawer', tinymce.plugins.ImageDrawerPlugin);
        tinymce.PluginManager.requireLangPack('imagedrawer');
    }

})();

