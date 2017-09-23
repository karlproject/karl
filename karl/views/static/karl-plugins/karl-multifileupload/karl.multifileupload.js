(function($){

var log = function() {
    if (window.console && console.log) {
        // log for FireBug or WebKit console
        console.log(Array.prototype.slice.call(arguments));
    }
};


/* XXX we repeat the namespace as a prefix of the name,
 * because ui creates a global jQuery plugin with the name
 * only */
$.widget('karl.karlmultifileupload', {

    options: {
        plupload_src: '',
        upload_url: ''
        // close: function(evt, data) {} // data is like: {refreshNeeded:..., runtime:...}
    },

    _create: function() {
        var self = this;
        this.refreshNeeded = false;
        this.reset_batch();

        var runtimes = 'html5,gears,flash,silverlight,html4';

        this.dialogSnippet = $(
            '<div class="karl-multifileupload-dialog-content">' +
                '<div class="uploader">' +
                    '<p>You browser doesn\'t have Flash, Silverlight, Gears, BrowserPlus or HTML5 support.</p>' + 
                '</div>' +
            '</div>'
        );
        this.dialogSnippet
            .appendTo('body')
            .hide()
            .karldialog({
                width: 800,
                open: function() {
                    // Must refresh the uploader for input shim and downloads handling
                    if (self.uploader) {
                         if (self._flash_closed) {
                            // recreate the uploader
                            self._bind_uploader(runtimes);
                            self._flash_closed = false;
                            log('Flash uploader recreated');
                        }
                        // change the logo in a way that the header text flows 
                        // right from the background image and centered vertically
                        // This is a bit tricky, but if it works well, it's worth it
                        // Note: this needs to be done on open and not on bind time,
                        // because Safari will not make the css style available at that time.
                        var header_content = self.dialogSnippet.find('.plupload_header_content');
                        if (! header_content.data('plupload_mogrified')) {
                            var actualimage_src = header_content.css('background-image').replace(/"/g,"").replace(/url\(|\)$/ig, "");
                            header_content.css('background-image', 'url()');
                            var actualimage = new Image();
                            actualimage.src = actualimage_src;
                            var table = $('<table></table>').insertBefore(header_content);
                            var tr = $('<tr></tr>').appendTo(table);
                            var td1 = $('<td valign="middle"></td>').appendTo(tr);
                            var td2 = $('<td valign="middle"></td>').appendTo(tr);
                            td1.append(actualimage);
                            td2.append(header_content);
                            header_content.data('plupload_mogrified', true);
                        }
                        //
                        // Refresh in any case
                        self.uploader.refresh();
                    }
                },
                close: function(evt) {
                    // XXX The flash uploader throws js error on IE, when
                    // hidden and shown again. So, we just throw it out...
                    // ... and recreate it if re-opened.
                    if (self.uploader.runtime == 'flash') {
                        log('Destroying flash uploader');
                        // Stop uploader and delete the flash element
                        self._flash_closed = true;
                        self.uploader.stop();
                        self.uploader.destroy();
                        self.plupload_widget.destroy();
                        setTimeout(function() {
                            // if the <OBJECT> is still there, kill it.
                            $(self.uploader.id + '_flash').remove();
                        }, 10);
                    }
                    // trigger the close event (with or without refresh)
                    self._trigger('close', evt, {
                        refreshNeeded: self.refreshNeeded,
                        runtime: self.uploader.runtime
                    });
                    // clear the flag
                    self.refreshNeeded = false;
                }
            });

        // create the uploader
        this._bind_uploader(runtimes);
    },
    
    _bind_uploader: function(runtimes) {
        var self = this;
        this.dialogSnippet
            .find('.uploader').plupload({
                // General settings
                runtimes: runtimes,
                url: this.options.upload_url,
                max_file_size: '100mb',
                // XXX Chunks are not supported right now - keep this commented
                chunk_size: '5mb',
                //unique_names: true,
                // multipart parameters
                multipart_params: {},
                // Flash settings
                flash_swf_url: this.options.plupload_src + '/js/plupload.flash.swf',
                // Silverlight settings
                silverlight_xap_url: this.options.plupload_src + '/js/plupload.silverlight.xap'
            });
        this.plupload_widget = this.dialogSnippet.find('.uploader').data('plupload');
        this.uploader = this.plupload_widget.uploader;
        // make plupload wrapper also have corners
        this.dialogSnippet.find('.plupload_container')
            .addClass('ui-corner-all');
        this.cancelButton = $('<a class="plupload_start plupload_dialog_close">Close</a>');
        this.cancelButton
            .insertAfter(this.dialogSnippet.find('.plupload_stop'))
            .button({
                icons: { primary: 'ui-icon-circle-close' }
            })
            .click(function() {
                self.close();
            });
        //
        this.uploader.bind('BeforeUpload', function(up, file) {
            // Extend form parameters dynamically
            var multipart_params = up.settings.multipart_params;
            // The batch ends when this is the last chunk of the last file
            // we set the parameter on all chunks of the last file, though,
            // because there seems to be no event for uploading a chunk.
            if (up.total.queued == 1) {
                multipart_params.end_batch = JSON.stringify(self.get_batch());
            } else {
                if (multipart_params.end_batch !== undefined) {
                    delete multipart_params.end_batch;
                }
            }
            // always send the client id
            // that we use to identify in case of errors
            multipart_params.client_id = file.id;
        });    
        this.uploader.bind('ChunkUploaded', function(up, file, response) {
                self.checkResponse(up, file, response);
                // Signal that we will need a refresh
                self.refreshNeeded = true;
        });
        this.uploader.bind('FileUploaded', function(up, file, response) {
                self.checkResponse(up, file, response);
                // Signal that we will need a refresh
                self.refreshNeeded = true;
        });
        this.uploader.bind('FilesAdded', function(up, files) {
            // XXX this is a bug in plupload???
            // It only happens with the flash backend.
            if (self.uploader.runtime == 'flash') {
                $.each(files, function(index) {
                    if (this.size === 0) {
                        // XXX This file has to be removed from the queue, else all is borked...
                        log('Zero-sized file problem, ignoring', this);
                        self.plupload_widget.removeFile(this.id);
                        var error_html = "<strong>Cannot upload a zero-sized file: " + this.name + "</strong><br>";
                        self.plupload_widget._notify('error', error_html); 
                    }
                });
            }
        });
    },

    destroy: function() {
        this.dialogSnippet.karldialog('destroy');
        this.uploader.stop();
        this.uploader.destroy();
        this.plupload_widget.destroy();
        $.Widget.prototype.destroy.call( this );
    },

    open: function() {
        this.dialogSnippet.karldialog('open');
    },
    
    close: function() {
        //self.uploader.stop();
        this.dialogSnippet.karldialog('close');
    },

    position: function(param) {
        return this.dialogSnippet
            .karldialog('position', param);
    },

    checkResponse: function(up, file, response) {
        // catch our custom error and react to it
        var data = JSON.parse(response.response);
        if (data.error) {
            var err_file;
            if (data.client_id) {
                // error in specific file
                // (due to batching, this may be a different one)
                err_file = up.getFile(data.client_id);
            } else {
                // no id in the response, we assume this is the same file then
                err_file = file;
            }
            var error_html = "<strong>Error during upload of " + err_file.name + ":</strong><br>" + data.error;
            this.plupload_widget._notify('error', error_html); 
            err_file.status = plupload.FAILED;
            this.plupload_widget._handleFileStatus(err_file);
            this.uploader.stop();
            this.reset_batch();
        } else {
            if (data.batch_completed) {
                this.reset_batch();
            } else {
                this.add_to_batch(file.id);
            }
        }
    },

    reset_batch: function() {
        // Start a new batch. Everything before this is gone...
        this._batch = [];
        this._batch_by_ids = {};
    },

    get_batch: function() {
        return this._batch;
    },

    add_to_batch: function(client_id) {
        // XXX with some runtimes, some event is triggered twice.
        // so we make sure we only enter each id once.
        if (this._batch_by_ids[client_id]) {
            return;
        }
        // Add this object to the batch.
        this._batch.push(client_id);
        this._batch_by_ids[client_id] = true;
    }

});

})(jQuery);

