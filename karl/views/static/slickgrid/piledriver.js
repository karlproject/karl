var dataView;
var grid;
var items;

function renderBenefits(row, cell, value, columnDef, dataContext) {
    var this_ul = $('<ul></ul>');
    $.each(value, function (index, item) {
        this_ul.append($('<li>' + item + '</li>'));
    });
    return this_ul.html();
}

function renderProject(row, cell, value, columnDef, dataContext) {
    // Title and Description
    var title = dataContext.title;
    var description = dataContext.description;
    this_cell = $('<div>');
    var kd = window._karl_client_data;
    var url = kd.wiki_url + dataContext.name;
    var hyperlink = '<a target="_newpage" href="' + url + '">' + title + '</a>';
    this_cell.append($('<div class="ag-projtitle">' + hyperlink + '</div>'));
    this_cell.append($('<div class="ag-projdesc">' + description + '</div>'));
    return this_cell.html();
}


var columns = [
    {id:"eval_date", name:"Eval Date", field:"eval_date", width:65,
        sortable:true, editor:AgilityCellEditor},
    {id:"title", name:"Project", field:"title", width:350, minWidth:300,
        cssClass:"cell-title", sortable:true, editor:AgilityCellEditor,
        formatter: renderProject},
    {id:"benefits", name:"Benefits", field:"benefits", sortable:false,
        width: 375, minWidth: 100, formatter:renderBenefits, editor:AgilityCellEditor},
    {id:"estimated", name:"Estimated", field:"estimated", sortable:true,
        width: 60, editor:AgilityCellEditor, groupTotalsFormatter: sumTotalsFormatter}

];

var options = {
    enableColumnReorder: false,
    enableCellNavigation: true,
    editable: true,
    asyncEditorLoading: false,
    rowHeight: 80,
    autoHeight: true,
    autoEdit: false
};

var sortcol = "title";
var sortdir = 1;
var searchString = "";

function titleFilter(item) {
    if (searchString != "" && item["title"].indexOf(searchString) == -1)
        return false;

    return true;
}

function comparer(a, b) {
    var x = a[sortcol], y = b[sortcol];
    return (x == y ? 0 : (x > y ? 1 : -1));
}

function reloadGrid(data) {
    items = data;
    dataView.beginUpdate();
    dataView.setItems(data);
    dataView.endUpdate();
}

function assignGrouping(dataView, config) {
    // The definition of what to group by is now defined server-side,
    // so we have to setup the grouping *after* fetching data.

    var group_by = config.group_by;
    var this_vocab = config.vocabularies[group_by];

    dataView.groupBy(
            group_by,
            function (g) {
                var sow = this_vocab[g.value];
                var counter = "  <span style='color:green'>(" + g.count + " items)</span>";
                return sow + counter;
            },
            function (a, b) {
                return a.value - b.value;
            }
    );

    dataView.setAggregators([
        new SumAggregator("estimated")
    ], false);

}

function loadSampleData() {
    var kd = window._karl_client_data;
    var url = kd.wiki_url + "get_agility_data.json";
    $.ajax({
                url: url,
                dataType: 'json',
                error: function (jqxhr, status, errorThrown) {
                    console.log("Error: " + errorThrown);
                },
                cache: false,
                success: function (data) {
                    reloadGrid(data.items);
                    assignGrouping(dataView, data.config);
                }});
}

$(function() {

    var groupItemMetadataProvider = new Slick.Data.GroupItemMetadataProvider();
    dataView = new Slick.Data.DataView({
                groupItemMetadataProvider: groupItemMetadataProvider
            });
    grid = new Slick.Grid("#ag-grid", dataView, columns, options);
    updateColumns();

    // register the group item metadata provider to add expand/collapse group handlers
    grid.registerPlugin(groupItemMetadataProvider);

    grid.setSelectionModel(new Slick.CellSelectionModel());

    grid.onSort.subscribe(function(e, args) {
        sortdir = args.sortAsc ? 1 : -1;
        sortcol = args.sortCol.field;

        dataView.sort(comparer, args.sortAsc);
    });

    // wire up model events to drive the grid
    grid.onCellChange.subscribe(function(e, args) {

        var kd = window._karl_client_data;
        var url = kd.wiki_url + "set_agility_data.json";
        $.ajax({
                    type: "POST",
                    url: url,
                    dataType: 'json',
                    data: JSON.stringify(args.item),
                    contentType: "application/json; charset=utf-8",
                    error: function (jqxhr, status, errorThrown) {
                        console.log("Error: " + errorThrown);
                    },
                    success: function (data) {
                        console.log("Saved");
                        dataView.updateItem(args.item.id, args.item);
                    }});
    });

    dataView.onRowCountChanged.subscribe(function(e, args) {
        grid.updateRowCount();
        grid.render();
    });

    dataView.onRowsChanged.subscribe(function(e, args) {
        grid.invalidateRows(args.rows);
        grid.render();
    });


    // wire up the search textbox to apply the filter to the model
    $("#txtSearch").keyup(function(e) {
        Slick.GlobalEditorLock.cancelCurrentEdit();

        // clear on Esc
        if (e.which == 27)
            this.value = "";

        searchString = this.value;
        dataView.refresh();
    });


    // initialize the model after all the events have been hooked up
    // $("#gridContainer").resizable();
    dataView.setFilter(titleFilter);
    loadSampleData();

    $('#ag-setup-btn').button();
    $('#ag-setup-btn').click(function () {
        $('#ag-grid').css('display', 'none');
        $('#ag-setup-frame').css('display', 'block');
    })

    $('#ag-setup-close').button();
    $('#ag-setup-close').click(function () {
        $('#ag-grid').css('display', 'block');
        $('#ag-setup-frame').css('display', 'none');
    })

});
