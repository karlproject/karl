

(function ($) {

  "use strict";

	$(function () {
		$('#tagbox').tagbox({
			prevals: window.head_data.panel_data.tagbox,
			validateRegexp: "^[a-zA-Z0-9\-\._]+$",
			searchTagURL: window.head_data.context_url + 'jquery_tag_search',
			addTagURL: window.head_data.context_url + 'jquery_tag_add',
			delTagURL: window.head_data.context_url + 'jquery_tag_del'
		});
	});

})(jQuery);