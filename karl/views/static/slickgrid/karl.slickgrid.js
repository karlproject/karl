/*

 SlickGrid components for KARL which are not specific to Agility

 */


function AgilityCellEditor(args) {
    var $input;
    var defaultValue;

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
        defaultValue = item[args.column.field] || "";
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

function SumAggregator(field) {
    var count;
    var nonNullCount;
    var sum;

    this.init = function() {
        count = 0;
        nonNullCount = 0;
        sum = 0;
    };

    this.accumulate = function(item) {
        var val = item[field];
        count++;
        if (val != null && val != NaN) {
            nonNullCount++;
            sum += 1 * val;
        }
    };

    this.storeResult = function(groupTotals) {
        if (!groupTotals.sum) {
            groupTotals.sum = {};
        }
        if (nonNullCount != 0) {
            groupTotals.sum[field] = sum;
        }
    };
}

function updateColumns() {
    // Iterate through all the columns and, if a column is enabled,
    // display the column.

    var visibleColumns = [];
    $('#ag-setup-columns')
            .find(":checkbox[id^=columnpicker]")
            .each(function(i,e) {
        if ($(this).is(":checked")) {
            visibleColumns.push(columns[i]);
        }
    });
    //grid.setColumns(visibleColumns);
}

function sumTotalsFormatter(totals, columnDef) {
    var str = "" + totals.sum[columnDef.field];
    return str.slice(0, 4);
}
