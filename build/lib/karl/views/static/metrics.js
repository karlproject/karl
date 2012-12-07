(function($) {

  var grid;

  var options = {
    enableCellNavigation: true,
    enableColumnReorder: true
  };

  $(function() {
    var table = $('table.metrics-grid').first();
    var columns = [];
    var colIndexToFieldMap = {};
    table.find('th').each(function(i) {
      var colText = $(this).text();
      var colId = colText.toLowerCase().replace(' ', '');
      var column = {
        id: colId,
        field: colId,
        name: colText,
        sortable: true
      };
      columns.push(column);
      colIndexToFieldMap['' + i] = colId;
    });

    var data = [];
    var uniqueId = 1;
    table.find('tbody tr').each(function() {
      var row = $(this);
      var rowData = {};
      row.find('td').each(function(colIdx) {
        var col = $(this);
        var fieldName = colIndexToFieldMap['' + colIdx];
        if (fieldName) {
          rowData[fieldName] = col.text();
        }
      });
      rowData.id = uniqueId++;
      data.push(rowData);
    });

    var dataView = new Slick.Data.DataView();
    var sortcol = 'contenttype';
    var comparer = function(a, b) {
      var x = a[sortcol], y = b[sortcol];
      var i = parseFloat(x), j = parseFloat(y);
      return (isNaN(i) || isNaN(j)
              ? (x == y ? 0 : (x > y ? 1 : -1))
              : (i == j ? 0 : (i > j ? 1 : -1)));
    };

    // we have width problems if we use a table element
    // replacing with a div seems to fix it
    var metricsGrid = $('<div />', {'class': 'metrics-grid'});
    table.replaceWith(metricsGrid);
    grid = new Slick.Grid(metricsGrid, dataView, columns, options);

    grid.onSort.subscribe(function(event, args) {
      grid.invalidate();
      grid.render();
      sortdir = args.sortAsc ? 1 : -1;
      sortcol = args.sortCol.field;

      // using native sort with comparer
      // preferred method but can be very slow in IE with huge datasets
      dataView.sort(comparer, args.sortAsc);

      grid.invalidateRows(args.rows);
      grid.render();
    });

    dataView.beginUpdate();
    dataView.setItems(data);
    dataView.endUpdate();
    grid.invalidate();
    grid.render();

  });
})(jQuery);
