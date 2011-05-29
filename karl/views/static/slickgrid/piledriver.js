var dataView;
var grid;
var sows;
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
    {id:"title", name:"Project", field:"title", width:395, minWidth:350,
        cssClass:"cell-title", sortable:true, editor:AgilityCellEditor,
        formatter: renderProject},
    {id:"benefits", name:"Benefits", field:"benefits", sortable:false,
        width: 340, minWidth: 100, formatter:renderBenefits, editor:AgilityCellEditor},
    {id:"sow", name:"SOW", field:"sow", width: 40, editor:AgilityCellEditor}
];

var options = {
    enableColumnReorder: false,
    enableCellNavigation: true,
    editable: true,
    enableAddRow: true,
    asyncEditorLoading: false,
    rowHeight: 80,
    autoHeight: true,
    autoEdit: false
};

var sortcol = "title";
var sortdir = 1;
var searchString = "";

function myFilter(item) {
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

function assignGrouping (dataView, config) {
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
}

function loadSampleData() {
    var kd = window._karl_client_data;
    var url = kd.wiki_url + "/get_agility_data.json";
    $.ajax({
                url: url,
                dataType: 'json',
                error: function (jqxhr, status, errorThrown) {
                    console.log("Error: " + errorThrown);
                },
                cache: false,
                success: function (data) {
                    assignGrouping(dataView, data.config);
                    reloadGrid(data.items);
                }});
}

$(function() {

    var groupItemMetadataProvider = new Slick.Data.GroupItemMetadataProvider();
    dataView = new Slick.Data.DataView({
                groupItemMetadataProvider: groupItemMetadataProvider
            });
    grid = new Slick.Grid("#myGrid", dataView, columns, options);

    // register the group item metadata provider to add expand/collapse group handlers
    grid.registerPlugin(groupItemMetadataProvider);

    grid.setSelectionModel(new Slick.CellSelectionModel());

    var columnpicker = new Slick.Controls.ColumnPicker(columns, grid, options);

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
    dataView.setFilter(myFilter);
    loadSampleData();


});

function AgilityCellEditor(args) {
    var $input;
    var defaultValue;
    var scope = this;

    this.xinit = function() {
        $input = $("<INPUT type=text class='editor-text' />")
                .appendTo(args.container)
                .bind("keydown.nav", function(e) {
            if (e.keyCode === $.ui.keyCode.LEFT || e.keyCode === $.ui.keyCode.RIGHT) {
                e.stopImmediatePropagation();
            }
        })
                .focus()
                .select();
    };

    this.init = function() {
        $input = $("<INPUT type=text class='editor-text' />")
                .appendTo(args.container)
                .bind("keydown.nav", function(e) {
            if (e.keyCode === $.ui.keyCode.LEFT || e.keyCode === $.ui.keyCode.RIGHT) {
                e.stopImmediatePropagation();
            }
        })
                .focus()
                .select();
    };

    this.destroy = function() {
        $input.remove();
    };

    this.focus = function() {
        $input.focus();
    };

    this.getValue = function() {
        return $input.val();
    };

    this.setValue = function(val) {
        $input.val(val);
    };

    this.loadValue = function(item) {
        var field = args.column.field;
        if (field == "title") {
            var t = item.title;
            var d = item.description;
            defaultValue = t + "||" + d;
        } else if (field == "benefits") {
            defaultValue = item.benefits.join("||");
        } else {
            defaultValue = item[args.column.field] || "";
        }
        $input.val(defaultValue);
        $input[0].defaultValue = defaultValue;
        $input.select();
    };

    this.serializeValue = function() {
        return $input.val();
    };

    this.applyValue = function(item, state) {
        var field = args.column.field;
        if (field == "title") {
            args.item.title = state.split("||")[0];
            args.item.description = state.split("||")[1];
        } else if (field == "benefits") {
            args.item.benefits = state.split("||");
        } else {
            item[args.column.field] = state;
        }

    };

    this.isValueChanged = function() {
        return (!($input.val() == "" && defaultValue == null)) && ($input.val() != defaultValue);
    };

    this.validate = function() {
        if (args.column.validator) {
            var validationResults = args.column.validator($input.val());
            if (!validationResults.valid)
                return validationResults;
        }

        return {
            valid: true,
            msg: null
        };
    };

    this.init();
}
