(function($) {

	$.extend($.ui.grid, {
		model: function(options) {
			options = $.extend({}, $.ui.grid.model.defaults, options);
			return {
				fetch: function(request, callback) {
					$.ajax($.extend(true, {
						url: options.url,
						data: request,
						success: function(response) {
							callback(options.parse(response));
						}
					}, options.ajax));
				}
			}
		}
	});

	$.ui.grid.model.defaults = {
		ajax: {
			dataType: "json",
			cache: false
		},
		parse: function(response) {
			var records = [];
			$.each(response.records, function() {
				var record = this;
				var result = {};
				$.each(response.columns, function(index) {
					result[this.id] = record[index];
				})
				records.push(result);
			});
			return {
				totalRecords: response.totalRecords,
				columns: response.columns,
				records: records
			};
		}
	}

})(jQuery);
