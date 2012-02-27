

(function ($) {

  "use strict";

	$(function () {
		$('#tagbox').tagbox({
			initialDataSource: window.head_data.panel_data.tagbox
		});
	});

})(jQuery);