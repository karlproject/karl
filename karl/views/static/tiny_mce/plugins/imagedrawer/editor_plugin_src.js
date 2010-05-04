
(function() {

    // unique id needed for the file upload input
    var next_fileinputid = 0;

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
                // Locate markup
                this.info_title = this.element.find('.tiny-imagedrawer-info-title');
                this.info_location = this.element.find('.tiny-imagedrawer-info-location');
                this.info_author = this.element.find('.tiny-imagedrawer-info-author');
                this.info_modified = this.element.find('.tiny-imagedrawer-info-modified');
                this.wrapper_location = this.element.find('.tiny-imagedrawer-info-location-wrapper');
                this.wrapper_author = this.element.find('.tiny-imagedrawer-info-author-wrapper');
                this.wrapper_modified = this.element.find('.tiny-imagedrawer-info-modified-wrapper');
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
                this.info_title.text(value.title || 'No selection');
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
                        $('<a></a>')
                            // XXX title should be limited (...)
                            .text(this.title)
                            .attr('href', this.href)
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
            }

        });

        $.extend($.tiny.imagedrawerinfopanel, {
                getter: "record",
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


    tinymce.create('tinymce.plugins.ImageDrawerPlugin', {

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
                
                // Do we need a dialog?
                if (! self.dialog) {
                    // Make a request to the server to fetch the dialog snippet
                    // as well as the initial batch of the image list
                    $.ajax({
                            type: 'GET',
                            url: ed.getParam('imagedrawer_dialog_url'),
                            data: '',
                            success: function(json) {self._dialogSuccess(json);},
                            error: function(json) {self._dialogError(json);},
                            dataType: 'json'
                        });

                        // XXX show loading status here?
                } else {
                    // Set the Insert/Replace button's text.
                    self._updateInsertReplaceState();
                    // We have it, so (re-)open it.
                    self.dialog.dialog('open');
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
            var upload_panel = this.dialog.find('.tiny-imagedrawer-panel-upload')
                .tiny_fixIEPanelSize($.tiny.PANEL_WD, $.tiny.PANEL_HD); // fix the box model if needed
            var external_panel = download_panel.find('.tiny-imagedrawer-panel-external')
                .tiny_fixIEPanelSize($.tiny.PANEL_WD, $.tiny.PANEL_HD); // fix the box model if needed
            this.images_panel = this.dialog
                .find('.tiny-imagedrawer-panel-images')
                .tiny_fixIEPanelSize($.tiny.PANEL_WD, $.tiny.PANEL_HD); // fix the box model if needed
            // source selection buttonset
            this.buttonset = this.dialog
                .find('.karl-buttonset.tiny-imagedrawer-buttonset-tabselect');
            this.buttonset
                .karlbuttonset({
                    clsContainer: 'tiny-imagedrawer-buttonset-tabselect'
                })
                .bind('change.karlbuttonset', function(event, button_index, value) {
                    // XXX TODO change this also to use sensible identifiers
                    // instead of indexes.
                    ////var target = (button_index != 0) ? download_panel : upload_panel;
                    if (value) {
                        ////target.show();
                       if (button_index == 0) {
                            // Handle the Upload tab
                            upload_panel.show();
                            self.images_panel.hide();
                            external_panel.hide();
                            // erase the info in the panel
                            self.info_panel.imagedrawerinfopanel('record', {});
                            self.selected_source = button_index;
                        } else if (button_index >= 1 && button_index <= 3) {
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
                            upload_panel.hide();
                            self.images_panel.show();
                            external_panel.hide();
                        } else if (button_index == 4) {
                            // Handle the External tab
                            upload_panel.hide();
                            self.images_panel.hide();
                            external_panel.show();
                            // erase the info in the panel
                            self.info_panel.imagedrawerinfopanel('record', {});
                            self.selected_source = button_index;
                        }
                    ////} else {
                    ////    target.hide();
                    }
                });
            this.selected_source = this.buttonset[0].selectedIndex; 
            // panels are shown based on initial selection
            // (Note: we use the index, not the option values,
            // which are irrelevant for the working of this code.)

            // XXX TODO switch from index to identifier here as well.

            if (this.selected_source == 0) {
                upload_panel.show();
                this.images_panel.hide();
                external_panel.hide();
            } else if (this.selected_source >= 1 && this.selected_source <= 3) {
                upload_panel.hide();
                this.images_panel.show();
                external_panel.hide();
            } else {
                upload_panel.hide();
                this.images_panel.hide();
                external_panel.show();
            }

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
                        self.dialog.dialog('close');
                    } else { // Cancel.
                        self.dialog.dialog('close');
                    }
                });

            // Wire up the external panel
            var urlinput = external_panel.find('.tiny-imagedrawer-urlinput');
            external_panel.find('.karl-buttonset.tiny-imagedrawer-buttonset-check')
                .karlbuttonset({
                    clsContainer: 'tiny-imagedrawer-buttonset-check'
                })
                .bind('change.karlbuttonset', function(event) {
                    // preload this image.
                    var image_url = urlinput.val();
                    // XXX TODO eventually, title could be calculated
                    // XXX from the image_url.
                    var title = 'External image';

                    var img = new Image();
                    var eventContext = {};
                    eventContext.thumb = self.external_stripe.insertRecord(0, 
                        {
                            loading: true,
                            title: title,
                            location: [{
                                title: image_url,
                                href: image_url
                                }]
                        }
                    );
                    // If we are on the external tab: select it,
                    // otherwise leave the active selection intact.
                    if (self.buttonset.val() == 'external') {
                        self._setSelection(eventContext.thumb);
                    }

                    $(img)
                        .attr('src', image_url)
                        .load(function() {
                            // update the record with the image sizes we have now
                            // and also set the thumbnail to show the image
                            eventContext.thumb.imagedrawerimage('record', $.extend({},
                                eventContext.thumb.imagedrawerimage('record'), {
                                    image_width: this.width,
                                    image_height: this.height,
                                    image_url: image_url,
                                    thumbnail_url: image_url
                            }));
                            // If there is no selection, and we are still on
                            // the upload tab: select it,
                            // otherwise leave the active selection intact.
                            if (self.buttonset.val() == 'external') {
                                if (self.selected_item == null) {
                                    self._setSelection(eventContext.thumb);
                                } else if (self.selected_item[0] === eventContext.thumb[0]) {
                                    // This is the selected item. Update the info panel.
                                    self._updateInfoPanel();
                                }
                            }
 
                        })
                        .error(function() {
                            // Get the existing data record and save the error in it.
                            eventContext.thumb.imagedrawerimage('record', 
                                $.extend(eventContext.thumb.imagedrawerimage('record'),
                                    {
                                        status: null,
                                        error: 'Wrong url, or not an image.',
                                        thumbnail_url: self.url + '/images/error.png'
                                    }
                                )
                            );
                            // If we are on that tab: select it regardless we have
                            // a current selection or not.
                            if (self.buttonset.val() == 'external') {
                                if (self.selected_item[0] === eventContext.thumb[0]) {
                                    // We are the selected item. Update the info panel.
                                    self._updateInfoPanel();
                                } else {
                                    self._setSelection(eventContext.thumb);
                                }
                            }
                        });
                });


            // Give the file input field a unique id
            this.fileinputid = 'tiny-imagedrawer-fileinputid-' + next_fileinputid;
            next_fileinputid += 1;
            var fileinput = this.dialog.find('.tiny-imagedrawer-fileinput');
            fileinput.attr('id', this.fileinputid);
            // Name is important as well!
            if (! fileinput.attr('name')) {
                // Give it default 'file', if it is not specified.
                // (Note, It will become the parameter name of the file
                // in the post.)
                fileinput.attr('name', 'file');
            }

            // Wire up the Upload button
            this.dialog
                .find('.karl-buttonset.tiny-imagedrawer-buttonset-upload')
                .karlbuttonset({
                    clsContainer: 'tiny-imagedrawer-buttonset-upload'
                })
                .bind('change.karlbuttonset', function(event, button_index, value) {
                    //if (button_index == 0) { // upload
                        // Signal the start of this upload
                        var eventContext = {};
                        self._uploadStart(eventContext);

                        // Initiate the upload
                        $.ajaxFileUpload({
                            url: ed.getParam('imagedrawer_upload_url'),
                            secureuri: false,
                            fileElementId: self.fileinputid,
                            extraParams: {
                                // extra parameters could be passed here with the upload.
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
                    //}
                });


            // Set the Insert/Replace button's text,
            // as well as the title on the top.
            this.title_tag = this.dialog
                .find('.tiny-imagedrawer-title');
            self._updateInsertReplaceState();

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
                    // Insert the selected one to the editor.
                    self._insertToEditor(this);
                    // And close the dialog.
                    self.dialog.dialog('close');
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
                .slider({
                    slide: function(e, ui) {
                        self._moveStripe(ui.value / 100);
                    }
                });

            // handle the stripe in the upload panel
            this.upload_stripe = new ImageStripe(
                upload_panel.find('ul.tiny-imagedrawer-imagestripe').eq(0),
                95, self.proto_image, {
                    title: self.editor.getLang('imagedrawer.loading_title'),
                    thumbnail_url: self.url + '/images/throbber.gif',
                    status: self.editor.getLang('imagedrawer.uploading_status')
                }
            );
            // Wire the scrollbar in the upload panel
            this.upload_scrollbar = upload_panel.find('.tiny-imagedrawer-scrollbar')
                .slider({
                    slide: function(e, ui) {
                        var stripe = self.upload_stripe;
                        var percentage_float = ui.value / 100;
                        var num_items = stripe.items().length;
                        // Move the stripe to a percentage position.
                        var slider_index = percentage_float * 
                                (num_items - self.visible_columns); 
                        if (slider_index < 0) {
                            // Region fits entirely without scrolling.
                            // Do nothing.
                            return;
                        }
                        ///
                        stripe.moveTo(slider_index);
                    }
                });

            // handle the stripe in the external panel
            this.external_stripe = new ImageStripe(
                external_panel.find('ul.tiny-imagedrawer-imagestripe').eq(0),
                95, self.proto_image, {
                    title: self.editor.getLang('imagedrawer.loading_title'),
                    thumbnail_url: self.url + '/images/default_image.png'
                }
            );
            // Wire the scrollbar in the external panel
            this.external_scrollbar = external_panel.find('.tiny-imagedrawer-scrollbar')
                .slider({
                    slide: function(e, ui) {
                        var stripe = self.external_stripe;
                        var percentage_float = ui.value / 100;
                        var num_items = stripe.items().length;
                        // Move the stripe to a percentage position.
                        var slider_index = percentage_float * 
                                (num_items - self.visible_columns); 
                        if (slider_index < 0) {
                            // Region fits entirely without scrolling.
                            // Do nothing.
                            return;
                        }
                        ///
                        stripe.moveTo(slider_index);
                    }
                });

            // Wire up the help panel
            var help_panel = this.dialog.find('.tiny-imagedrawer-panel-help')
                .hide();
            help_panel.find('.karl-buttonset')
                .karlbuttonset({})
                .bind('change.karlbuttonset', function(event, button_index, value) {
                    help_panel.hide('slow');
                    download_panel.show('slow');
                });
            this.dialog.find('.tiny-imagedrawer-button-help')
                .click(function(event) {
                    help_panel.show('fold');
                    download_panel.hide('fold');
                    event.preventDefault();
                });


            // Check that the slider is either jquery ui version 1.8,
            // or that the code is patched with 1.7.
            // The bug in question would prevent the slider to ever go
            // back to value 0.
            if ($.ui.version < '1.8' && ! this.scrollbar.data('slider')._uiHash_patched) {
                throw new Error('jquery-ui version >= 1.8, or patched 1.7 version required.');
            }
            
            //
            // Render the first batch of images
            //
            if (json.images_info) {
                this._initImages(json.images_info);
                this._loadRecords(json.images_info);
            }

            // force initial selection to null 
            self._setSelection(null);

            // Finally, open the dialog.
            this.dialog.dialog('open');
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
            this._moveStripe(this.scrollbar.slider('value') / 100);
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
            var ed = this.editor;
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
            // Insert the image data into the editor
            eventContext.thumb = this.upload_stripe.insertRecord(0, 
                {
                    loading: true,
                    title: '' + document.getElementById(this.fileinputid).value
                });
            // If we are on the upload tab
            // (most likely the case): select it,
            // otherwise leave the active selection intact.
            if (this.buttonset.val() == 'uploadnew') {
                this._setSelection(eventContext.thumb);
            }
        },

        _uploadSuccess: function(json, eventContext) {
            var self = this;
            var ed = this.editor;
            // use error sent by server, if available
            var error = json && json.error;
            if (error) {
                this._uploadError(json, eventContext);
                return;
            }

            // Update the image data that just arrived
            eventContext.thumb
                .imagedrawerimage('record', json.upload_image_info);
            //this._moveStripe(this.scrollbar.slider('value') / 100);
            //
            // If there is no selection, and we are still on
            // the upload tab: select it,
            // otherwise leave the active selection intact.
            if (this.buttonset.val() == 'uploadnew') {
                if (this.selected_item == null) {
                    this._setSelection(eventContext.thumb);
                } else if (this.selected_item[0] === eventContext.thumb[0]) {
                    // This is the selected item. Update the info panel.
                    this._updateInfoPanel();
                }
            }
        },

        _uploadError: function(json, eventContext) {
            // use error sent by server, if available
            var error = json && json.error;
            if (! error) {
                error = 'Server error when fetching drawer_upload_view.html';
            }
            // Get the existing data record and save the error in it.
            eventContext.thumb.imagedrawerimage('record', 
                $.extend(eventContext.thumb.imagedrawerimage('record'),
                    {
                        status: null,
                        error: '' + error,
                        thumbnail_url: this.url + '/images/error.png'
                    }
                )
            );
            // If we are on that tab: select it regardless we have
            // a current selection or not.
            if (this.buttonset.val() == 'uploadnew') {
                if (this.selected_item[0] === eventContext.thumb[0]) {
                    // We are the selected item. Update the info panel.
                    this._updateInfoPanel();
                } else {
                    this._setSelection(eventContext.thumb);
                }
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
            this.scrollbar.slider('value', 0);
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
            var self = this;
            // load the required data
            var region_id = this.region_id;
            $.ajax({
                type: 'GET',
                url: this.editor.getParam('imagedrawer_data_url'),
                data: {
                    start: start, 
                    limit: limit,
                    sort_on: 'creation_date',
                    reverse: '1',
                    source: this.buttonset.val()
                },
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

            var dimension = $("select[name=tiny-imagedrawer-input-dimension]").val();
            var align = $("input:radio[name=tiny-imagedrawer-input-align]:checked").val();

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
            }[dimension];
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

            var args = {
                src: record.image_url,
                align: align,
                width: width,
                height: height

                // constrain (bool)
                // vspace
                // hspace
                // border
                // alt
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
            } else {
                // We are inserting a new image.
                ed.execCommand('mceInsertContent', false, '<img id="__mce_tmp" />', {skip_undo : 1});
                ed.dom.setAttribs('__mce_tmp', args);
                ed.dom.setAttrib('__mce_tmp', 'id', '');
                ed.undoManager.add();
            }


        },

        // Either return the selected image in the editor, or null, in case we are replacing.
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

        _updateInsertReplaceState: function() {
            var title;
            var button_label;
            if (this._getEditorImageSelection()) {
                title = 'Replace Image';
                button_label = 'Replace';
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
    tinymce.PluginManager.add('imagedrawer', tinymce.plugins.ImageDrawerPlugin);
    tinymce.PluginManager.requireLangPack('imagedrawer');

})();

