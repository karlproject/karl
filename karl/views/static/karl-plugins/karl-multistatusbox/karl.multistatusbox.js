
(function($){


$.widget('karl.multistatusbox', {
 
    options: {
        clsContainer: 'ui-widget',
        clsItem: 'ui-state-highlight ui-corner-all',
        hasCloseButton: true
    },
   
    _create: function() {
        // initialize the queue
        this.queue = [];
        // add container class to container
        this.element.addClass(this.options.clsContainer);
    },

    /*
     * Public methods
     **/

    /* Clear all messages, or all messages with a given queueCategory */
    clear: function(/*optional*/ queueCategory) {
        if (queueCategory === undefined) {
            // shortcut: clear all items
            this.element.empty();
            this.queue = [];
        } else {
            // Clear items of the given category
            var newQueue = [];
            $(this.queue).each(function() {
                // The element may have been deleted (by closebutton),
                // but we don't check for this, since remove() works
                // safe with elements already removed.
                if (this.queueCategory == queueCategory) {
                    this.item.remove();
                } else {
                    // keep item in queue
                    newQueue.push(this);
                }
            });
            this.queue = newQueue;
        }
    },

    /* Append a message */
    append: function(message, /*optional*/ queueCategory, clsItem) {
        // default queue category is null.
        if (queueCategory === undefined) {
            queueCategory = null;
        }
        // Append the item
        var item = $('<div class="karl-multistatusbox-item ui-helper-clearfix"></div>');
        // Add item classes to the item
        if (clsItem === undefined) {
            clsItem = this.options.clsItem;
        }
        item.addClass(clsItem);
        // Create message and (if needed) a close button
        item.append($('<div class="karl-multistatusbox-message"></div>').append(message));
        if (this.options.hasCloseButton) {
            item.append($('<a href="#" class="karl-multistatusbox-closebutton">' + 
                          '<span class="ui-icon ui-icon-closethick">X</span></a>')
                        .hover(
                            function(e) { $(this).addClass('ui-state-hover'); },
                            function(e) { $(this).removeClass('ui-state-hover'); }
                        )
                        .click(function(e) {
                            item.remove();    
                            e.preventDefault();
                        })
            );
        }
        this.element.append(item);
        // Remember it on the queue
        this.queue.push({
            item: item,
            queueCategory: queueCategory
        });
    },

    /* Append a message after clearing previous messages.
     * If queueCategory is specified, only the messages added with the
     * same category are cleared. */
    clearAndAppend: function(message, /*optional*/ queueCategory, clsItem) {
        this.clear(queueCategory);
        this.append(message, queueCategory, clsItem);
    }


    /*
     * Private methods
     **/


});

})(jQuery);

