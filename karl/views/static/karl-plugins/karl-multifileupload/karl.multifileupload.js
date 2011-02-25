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

        var dialogSnippet = this.dialogSnippet = $(
            '<div class="karl-multifileupload-dialog-content">' +
                '<div class="uploader">' +
                    '<p>You browser doesn\'t have Flash, Silverlight, Gears, BrowserPlus or HTML5 support.</p>' + 
                '</div>' +
            '</div>'
        );
        dialogSnippet
            .hide()
            .appendTo('body')
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
                    if (self.uploader) {
                        self.uploader.refresh();
                    }
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
                runtimes: 'html5,browserplus,gears,flash,silverlight',
                url: this.options.upload_url,
                max_file_size: '100mb',
                // XXX Chunks are not supported right now - keep this commented
                //chunk_size: '1mb',
                //unique_names: true,
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
        var data = $.parseJSON(response.response);
        if (data.error) {
            var error_html = "<strong>Error during upload of " + file.name + ":</strong><br>" + data.error;
            this.plupload_widget._notify('error', error_html); 
            file.status = plupload.FAILED;
            this.plupload_widget._handleFileStatus(file);
            this.uploader.stop();
        }
    }

});

})(jQuery);

