
Karl.content_feeds = {
    init: function () {
        var self = Karl.content_feeds;

        this._base_url = '/newest_feed_items.json';
	this._templates = {};
        if ($('#filter').text() != '') {
            this._url = this._base_url + '?filter=' + $('#filter').text();
        } else {
            this._url = this._base_url;
        };
	// Valid states are: 'on', 'off', 'polling', 'error'
	this._ajax_state = 'on';

	$("#polling-info").click(function() {
		$(".polling-details.info").fadeIn("fast");
	    });
	$(".polling-details .close").click(function() {
		$(".polling-details").fadeOut("fast");
	    });

	// On-off indicator
	$("#poll-indicator.on, #poll-indicator.polling").live('click', function() {
		$("#poll-indicator").attr("class","off");
		self.setAjaxState('off');
	    });
	$("#poll-indicator.off").live('click', function() {
		$("#poll-indicator").attr("class","on");
		self.setAjaxState('on');
	    });

	// Error indicator
	$("#poll-indicator.error").live('click', function() {
		$(".polling-details.errormessage").fadeIn("fast");
	    });

    },

    get_items: function (url) {
	// Custom version of getJSON, with error handling, making sure
	// only one request is active at a time.
        var self = Karl.content_feeds;

	// Parse state and decide whether to issue request.  If we are
	// 'off', 'polling', or 'error', bail out.
	var states = ['off', 'polling', 'error'];
	if (jQuery.inArray(self._ajax_state, states) > -1) {
	    //console.log('bailout: ' + self._ajax_state);
	    return;
	};

	self.setAjaxState('polling');
	return jQuery.ajax({
		type: "GET",
		url: self._url,
		success: self._ajaxSuccess,
		error: self._ajaxError,
		dataType: 'json'
		    });
    },

    _getTemplate: function (key) {
	// Pre-compile and cache templates
        var self = Karl.content_feeds;

	var template = self._templates[key];
	if (template == null) {
	    template = tmpl(key);
	    self._templates[key] = template;
	}

	return template;
    },

    _ajaxSuccess: function (data) {

	// Bind some vars
	var self = Karl.content_feeds;
	var last_gen = data[0];
	var last_index = data[1];
	var earliest_gen = data[2];
	var earliest_index = data[3];
	var rows = data[4];
	var item_row = self._getTemplate('item_row');

	var insert_mark = $('#feedlist');
	var append = true;
	if ($('#feedlist').children().length > 0) {
	    insert_mark = $($('#feedlist').children()[0]);
	    append = false;
	}
	$.each(rows, function (key, row) {
		var flavor = self._getTemplate(row.flavor);
		row['flavor'] = flavor({item: row});
                if (!append) {
		    insert_mark.before(item_row({item: row}));
                } else {
		    insert_mark.append(item_row({item: row}));
                }
	});
	$('#last_gen').text(last_gen);
	$('#last_index').text(last_index);

	$('#polled').text(new Date().toString());
	$('abbr.timeago').timeago();

	// Update the URL used on next JSON request
	var new_url = self._base_url + '?newer_than='
	              + last_gen + ':' + last_index;
	if ($('#filter').text() != '') {
	    new_url = new_url + '&filter='+$('#filter').text();
	};
	$('#json_feed_url').text(new_url);
	$('#json_feed_url').attr('href', new_url);

	self._url = new_url;
	self._last_gen = last_gen;
	self._last_index = last_index;
    if (self._earliest_gen) {
        self._earliest_gen = Math.min(self._earliest_gen, earliest_gen);
        self._earliest_index = Math.min(self._earliest_index, earliest_index);
    } else {
        self._earliest_gen = earliest_gen;
        self._earliest_index = earliest_index;
    };
	self.setAjaxState('on');
    },

    _ajaxError: function (xhr, textStatus, errorThrown) {
        var self = Karl.content_feeds;

	//console.log('error: ' + textStatus);
	self.setAjaxState('error');
	var msg = textStatus + ": " + xhr.statusText;
	$('#kf-errordetail').text(msg);
    },

    setFilter: function (filter, selected) {
        var self = Karl.content_feeds;
        $('#feedlist').empty();
        $('#filter').text(filter);
        self._url = self._base_url + '?filter=' + filter;
        $('.filterlink').parent().removeClass('current');
        selected.addClass('current');
        self.get_items();
    },

    setAjaxState: function (newstate) {
	// Set state and possibly update UI
        var self = Karl.content_feeds;

	//console.log('Changing state from "' + self._ajax_state + 
	//	    '" to "' + newstate + '"');
	var indicator = $('#poll-indicator');
	if (indicator.hasClass(self._ajax_state)) {
	    indicator.removeClass(self._ajax_state);
	}
	self._ajax_state = newstate;
	indicator.addClass(self._ajax_state);
    }

};


$(document).ready(function(){
    Karl.content_feeds.init();
    Karl.content_feeds.get_items();
    $('.filterlink').bind('click', function(e) {
        Karl.content_feeds.setFilter(this.rel, $(this).parent());
        return false;
    });
    setInterval('Karl.content_feeds.get_items()', 30000);
});
