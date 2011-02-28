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
    },

    _create: function() {
        var self = this;
        this.refreshNeeded = false;
        this.reset_batch();

        //var runtimes = 'html5,browserplus,gears,flash,silverlight';
        var runtimes = 'html5,browserplus,gears,silverlight,html4';
        if ($.browser.webkit) {
            // html5 borken on Safari
            runtimes = 'browserplus,gears,silverlight,flash,html4';
        }

        var dialogSnippet = this.dialogSnippet = $(
            '<div class="karl-multifileupload-dialog-content">' +
                '<div class="uploader">' +
                    '<p>You browser doesn\'t have Flash, Silverlight, Gears, BrowserPlus or HTML5 support.</p>' + 
                '</div>' +
            '</div>'
        );
        dialogSnippet
            .appendTo('body')
            .hide()
            .karldialog({
                width: 800,
                open: function() {
                    // Must refresh the uploader for input shim and downloads handling
                    if (self.uploader) {
                        self.uploader.refresh();
                    }
                },
                close: function() {
                    // Make sure that the dialog always gets refreshed
                    // when the dialog is closed (incl. ESC, and all)
                    // XXX causes problem in IE
                    //if (self.uploader) {
                    //    self.uploader.refresh();
                    //}
                    // Do we need a refresh?
                    if (self.refreshNeeded) {
                        // trigger the event
                        self.element.trigger('refresh.multifileupload');
                        // clear the flag
                        self.refreshNeeded = false;
                    }
                }
            })
            .find('.uploader').plupload({
                // General settings
                runtimes: runtimes,
                url: this.options.upload_url,
                max_file_size: '100mb',
                // XXX Chunks are not supported right now - keep this commented
                chunk_size: '100mb',
                //unique_names: true,
                // multipart parameters
                multipart_params: {},
                // Flash settings
                flash_swf_url: this.options.plupload_src + '/js/plupload.flash.swf',
                // Silverlight settings
                silverlight_xap_url: this.options.plupload_src + '/js/plupload.silverlight.xap'
            });
        // make plupload wrapper also have corners
        dialogSnippet.find('.plupload_container')
            .addClass('ui-corner-all');
        this.plupload_widget = dialogSnippet.find('.uploader').data('plupload');
        this.uploader = this.plupload_widget.uploader;
        this.cancelButton = $('<a class="plupload_start plupload_dialog_close">Close</a>');
        this.cancelButton
            .insertAfter(dialogSnippet.find('.plupload_stop'))
            .button({
                icons: { primary: 'ui-icon-circle-close' }
            })
            .click(function() {
                self.close();
            });
        this.uploader.bind('UploadFile', function(up, file) {
            // Extend form parameters dynamically
            var multipart_params = up.settings.multipart_params;
            if (up.total.queued == 1) {
                multipart_params.end_batch = JSON.stringify(self._batch);
                log('UploadFile last!', multipart_params);
            } else {
                if (up.settings.multipart_params.end_batch !== undefined) {
                    delete up.settings.multipart_params.end_batch;
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
            // XXX this is a bug in plupload??? ... appears with an extension .screenflow on html5... ???
            $.each(files, function(index) {
                if (this.size === 0) {
                    // XXX This file has to be removed from the queue, else all is borked...
                    log('XXX extension problem', this);
                    self.plupload_widget.removeFile(this.id);
                    var error_html = "<strong>Unkown error adding: " + this.name + "</strong><br>";
                    self.plupload_widget._notify('error', error_html); 
                }
            });
        });
    },
    
    destroy: function() {
        this.dialogSnippet.karldialog('destroy');
        //self.uploader.stop();

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
                // we should have received a tmp_id.
                this.add_to_batch(data.temp_id, file.id);
            }
        }
    },

    reset_batch: function() {
        // Start a new batch. Everything before this is gone...
        this._batch = [];
        this._batch_by_ids = {};
    },

    add_to_batch: function(temp_id, client_id) {
        // XXX A bug...? with some runtimes, this event is triggered twice.
        if (this._batch_by_ids[client_id]) {
            return;
        }
        // Add this object to the batch.
        var info = {temp_id: temp_id, client_id: client_id};
        this._batch.push(info);
        this._batch_by_ids[client_id] = info;
    }

});

})(jQuery);

