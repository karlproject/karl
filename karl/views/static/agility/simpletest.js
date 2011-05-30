
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
        sortable:true},
    {id:"title", name:"Project", field:"title", width:340, minWidth:300,
        cssClass:"cell-title", formatter: renderProject, sortable:true}
];

var options = {
    enableCellNavigation: true,
    enableColumnReorder: false
};

function reloadGrid(data) {
    items = data;
    dataView.beginUpdate();
    dataView.setItems(data);
    dataView.endUpdate();
}


function loadSampleData() {
    var url = "get_agility_data.json";
    $.ajax({
                url: url,
                dataType: 'json',
                error: function (jqxhr, status, errorThrown) {
                    console.log("Error: " + errorThrown);
                },
                cache: false,
                success: function (data) {
                    reloadGrid(data.items);
                }});
}
$(function() {

    var groupItemMetadataProvider = new Slick.Data.GroupItemMetadataProvider();
    dataView = new Slick.Data.DataView({
                groupItemMetadataProvider: groupItemMetadataProvider
            });
    grid = new Slick.Grid("#ag-grid", dataView, columns, options);

    dataView.onRowCountChanged.subscribe(function(e, args) {
        grid.updateRowCount();
        grid.render();
    });

    dataView.onRowsChanged.subscribe(function(e, args) {
        grid.invalidateRows(args.rows);
        grid.render();
    });

    loadSampleData();


})
