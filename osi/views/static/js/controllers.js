var app = angular.module("pdcApp", []);

// Awesome, JS doesn't let you delete an array item
Array.prototype.removeItem = function (val) {
    var arr = this;
    for (var i = 0, j = 0, l = arr.length; i < l; i++) {
        if (arr[i] !== val) {
            arr[j++] = arr[i];
        }
    }
    arr.length = j;
};

function formattedDate(date) {

    var yyyy = date.getFullYear().toString();
    var mm = (date.getMonth() + 1).toString(); // getMonth() is zero-based
    var dd = date.getDate().toString();
    var HH = date.getHours().toString();
    var MM = date.getMinutes().toString();
    var SS = date.getSeconds().toString();

    return yyyy + '-' + (mm[1] ? mm : "0" + mm[0]) + '-' + (dd[1] ? dd : "0" + dd[0])
        + ' ' + (HH[1] ? HH : "0" + HH[0] )
        + ':' + (MM[1] ? MM : "0" + MM[0])
        + ':' + (SS[1] ? SS : "0" + SS[0]);
};
function LayoutView($http, $scope, traverser) {

    // A helper
    function inbound_cleanup(resource) {
        /* Callback to re-arrange JSON data during walking */

        // If a report, extract the various category stuff (e.g.
        // departments, etc.) into proper attrs
        if (resource.type == 'report') {
            resource.items.forEach(function (i) {
                // If this items has itself an items array, make a
                // property on the resource with that item.name and
                // set that property's value to this item's values,
                // for example: resource.entities = []
                if (i.type == "filter-category") {
                    resource[i.name] = i.values;
                } else if (i.type == "mailinglist") {
                    resource.mailinglist = i.short_address;
                } else {
                    console.log("Unknown item type:", i.type)
                }
            });

            // Just to be sure, remove the .items
            delete resource.items;
        }
    }

    $scope.update_site = function () {
        // User clicks the Update button, first flatten the site data
        // to remove cycles

        var prop;
        var flagged_props = ['parent', 'resource_url'];
        var special_props = ['departments', 'offices', 'entities', 'boards'];

        function walk_tree(resource) {

            // Make a copy of this object, without the internal
            // properties such as parent or resource_url
            var new_resource = {};
            for (prop in resource) {
                if (!_.contains(flagged_props, prop)) {
                    new_resource[prop] = resource[prop];
                }
            }

            // Put the special entities back in
            if (new_resource.type == "report") {
                new_resource.items = [];
                if (new_resource.hasOwnProperty('mailinglist')) {
                    new_resource.items.push({type: "mailinglist", name: "mailinglist",
                                                short_address: new_resource.mailinglist});
                    delete new_resource['mailinglist'];
                }
                special_props.forEach(function (sp) {
                    if (new_resource.hasOwnProperty(sp)) {
                        if (new_resource[sp].length != 0) {
                            // Only push new item if property not empty
                            new_resource.items.push({
                                                        name: sp,
                                                        type: "filter-category",
                                                        values: new_resource[sp]
                                                    });
                        }
                        // Now remove this from being stored directly
                        // on the new_resource
                        delete new_resource[sp];
                    }
                });
            }

            // If there are children, recurse into them
            if (resource.hasOwnProperty('items')) {
                new_resource.items = [];
                resource.items.forEach(function (item) {
                    new_resource.items.push(walk_tree(item));
                })
            }

            return new_resource;
        }

        var categories = angular.copy(traverser.root.categories);
        var sections = walk_tree(traverser.root);
        var put_data = {
            "sections": sections.items,
            "categories": categories
        };

        // Get the URL to save data back to, then save
        var json_url = $("#main-view").data("traversal-json-url");
        return $http.put(json_url, put_data)
            .success(function () {
                         traverser.setDirty(false);
                     })
            .error(function (data, status, headers) {
                       var msg = "Failed to save data to " + json_url;
                       traverser.setWarning(msg);
                       console.log('Failed to save data:', status, headers);
                   })
    };

    // Load and massage the People JSON
    var new_data;
    $scope.load_data = function () {
        var json_url = $("#main-view").data("traversal-json-url");
        $http.get(json_url)
            .success(function (data) {
                         // Massage the data a little
                         $scope.vocabs = {
                             columns: ["name", "position",
                                 "location", "phone", "email"]
                         };
                         data.categories.forEach(function (i) {
                             $scope.vocabs[i.name] = i.values;
                         });

                         new_data = {
                             "title": "PDC",
                             "type": "SiteRoot",
                             "items": data.sections,
                             "categories": data.categories
                         };

                         traverser.setRoot(new_data,
                                           [inbound_cleanup]);
                     })
            .error(function () {
                       traverser.warning = "Failed to load data from: " + json_url;
                   })
    };
    $scope.load_data();

    $scope.set_dirty = function () {
        traverser.setDirty(true);
    };

    $scope.is_nav = function (section) {
        // Make sure we're bootstrapped and have a context

        if (traverser.context) {
            var rul = traverser.context.resource_url;

            if (section == '/') {
                // We special case this, only match on exact match
                return section == rul ? 'active' : '';
            } else if (rul.substring(0, section.length) === section) {
                return "active";
            }
        }
    };


    $scope.clear_warning = function () {
        /* If something sets a warning, the box shows with a button
         to clear the warning. */
        traverser.setWarning("");
    };

    /* When the traverser changes (data loaded, user goes to a
     different location), recalculate the breadcrumbs */
    $scope.$on("traverserChanged", function (event, context) {

        // Calculate breadcrumbs
        var breadcrumbs = [];
        traverser.parents.forEach(function (item) {
            breadcrumbs.push(item)
        });
        breadcrumbs.push(context);
        $scope.breadcrumbs = breadcrumbs;

        // Clear the preview, if any
        $scope.preview_data = null;
    });

    $scope.preview_report = function (context) {
        /* Given some configuration options, return the results */

        var preview_url = $("#main-view").data("preview-json-url");

        var qs = 'columns=' + context.columns.join(',');
        ['offices', 'departments', 'entities', 'boards'].forEach(function (i) {
            if (context[i] && context[i].length == 1) {
                // One value, no :or needed
                qs += "&category_" + i + "=";
                qs += context[i].join(",");
            } else if (context[i] && context[i].length > 1) {
                // More than one value, :or needed
                qs += "&category_" + i + "=";
                qs += context[i].join(",") + ":or";
            }
        });
        $http.get(preview_url + "?" + qs)
            .success(function (data) {
                         $scope.preview_data = {
                             columns: context.columns,
                             items: data.records
                         };
                     })
            .error(function () {
                       traverser.warning = "Failed to load data from: " + preview_url;
                   });
    }

    $scope.available_css_classes = ['general', 'priority'];

    var mv = $('#main-view');
    $scope.partials_prefix = mv.data('partials-prefix');

    /* #######      End LayoutView      ########## */

}

function SiteRootView($scope, storage, $http, traverser) {
    var json_url = $("#main-view").data("traversal-json-url");

    storage.bind($scope, "snapshots");
    if (!$scope.snapshots) {
        // Initialize
        $scope.snapshots = [];
    }
    $scope.make_snapshot = function () {
        var label = $('#inputLabel').val();
        var timestamp = formattedDate(new Date());
        console.log("### Making snapshot");

        $http.get(json_url)
            .success(function (data) {
                         $scope.snapshots.push({
                                                   label: label,
                                                   timestamp: timestamp,
                                                   json: data
                                               });
                         $('#inputLabel').val("");
                     });
    }
    $scope.restore_snapshot = function (snapshot_id) {
        var snapshot = $scope.snapshots.findByProp("timestamp", snapshot_id);
        var snapshot_data = snapshot.json;

        return $http.put(json_url, snapshot_data)
            .success(function () {
                         $scope.load_data();
                     })
            .error(function (data, status, headers) {
                       var msg = "Failed to save data to " + json_url;
                       traverser.setWarning(msg);
                       console.log('Failed to save data:', status, headers);
                   })

    }

    $scope.remove_snapshot = function (snapshot_id) {
        $scope.snapshots = $scope.snapshots.filter(function (i) {
            return i.timestamp != snapshot_id;
        });
    }
    $scope.clear_all = function () {
        $scope.snapshots = [];
    }
}

function SectionView($scope, storage) {
    storage.bind($scope, "snapshots");
}

function ColumnView() {
}

function ReportGroupView() {
}

function ReportEditView($scope, traverser, $location) {
    $scope.report_title = 'Edit ' + traverser.context.title;
    $scope.mode = 'edit';
    $scope.context = _.omit(traverser.context, 'parent');

    $scope.has_mailinglist = true ? $scope.context.hasOwnProperty("mailinglist") : false;

    // Mailing list support is a little more complex, we need a
    // checkbox AND an input box that defaults to the correct value
    $scope.toggle_mailinglist = function () {
        if ($scope.has_mailinglist) {
            // Enable mailing list, set input box value to
            // default to context.name
            $scope.context.mailinglist = $scope.context.name;
        } else {
            // Disable mailing list, clean out the value
            delete $scope.context.mailinglist;
        }
    };

    $scope.updateReport = function () {

        // Copy the props out of context back into traverser.context
        for (var prop in $scope.context) {
            traverser.context[prop] = $scope.context[prop];
        }

        // Remove the mailing list if necessary
        if ($scope.has_mailinglist == false) {
            delete traverser.context.mailinglist;
        }

        traverser.setDirty(true);
        $location.path(traverser.context.parent.resource_url);
    };

    $scope.resetReport = function () {
        $scope.context = _.omit(traverser.context, 'parent');
    };

    $scope.cancel = function () {
        // Clean up and go back to previous view
        delete $scope.context;
        $location.path(traverser.context.parent.resource_url);
    };
    $scope.deleteReport = function () {

        var parent = traverser.context.parent;
        traverser.context.parent.items.removeItem(traverser.context);
        delete $scope.context;
        traverser.setDirty(true);
        $location.path(parent.resource_url);
    };

    $scope.update_name = function () {
        // When the title changes, if the name field is empty,
        // propose a lower-case-hyphen-spaced
        if (!$scope.context.name) {
            var t = $scope.context.title;
            $scope.context.name = t.replace(' ', '-').toLowerCase();
        }
    };
}


function ReportAddView($scope, traverser, $location) {
    var parent = traverser.context;
    var rul;
    $scope.report_title = "Add Report";
    $scope.mode = "add";
    var blank_context = {
        "type": "report", "css_class": "general", "columns": []
    };
    $scope.context = angular.copy(blank_context);
    $scope.has_mailinglist = false;

    // Mailing list support is a little more complex, we need a
    // checkbox AND an input box that defaults to the correct value.
    $scope.toggle_mailinglist = function () {
        if ($scope.has_mailinglist) {
            // Enable mailing list, set input box value to
            // default to context.name
            $scope.context.mailinglist = $scope.context.name;
        } else {
            // Disable mailing list, clean out the value
            delete $scope.context.mailinglist;
        }
    };

    $scope.update_name = function () {
        // When the title changes, if the name field is empty,
        // propose a lower-case-hyphen-spaced
        if (!$scope.context.name) {
            var t = $scope.context.title;
            $scope.context.name = t.replace(/ /g, '-').toLowerCase();
        }

        // Also update Link Title if it is empty
        if (!$scope.context.link_title) {
            $scope.context.link_title = $scope.context.title;
        }
    };

    $scope.updateReport = function () {
        // Remove the mailing list if necessary
        if ($scope.has_mailinglist == false) {
            delete $scope.context.mailinglist;
        }
        parent.items.push($scope.context);
        $scope.context.parent = parent;
        rul = parent.resource_url + $scope.context.name + '/';
        $scope.context.resource_url = rul;
        traverser.setDirty(true);
        $location.path(parent.resource_url);

    };

    $scope.resetReport = function () {
        $scope.context = angular.copy(blank_context);
    };

    $scope.cancel = function () {
        // Clean up and go back to previous view
        delete $scope.context;
        $location.path(parent.resource_url);
    };
}