var app = angular.module("pdcApp", ['traversal', 'ui.router',
    'ui.sortable', 'ui.select2', 'angularLocalStorage']);

app.config(function ($stateProvider) {

    var partials_prefix = $("#main-view").data("partials-prefix");

    $stateProvider
        .state('layout', {
                   abstract: true,
                   templateUrl: partials_prefix + "/layout.html",
                   controller: LayoutView
               })
        .state('siteroot-default', {
                   url: '*path',
                   parent: "layout",
                   controller: SiteRootView,
                   templateUrl: partials_prefix + "/siteroot_view.html"
               })
        .state('section-default', {
                   parent: "layout",
                   controller: SectionView,
                   templateUrl: partials_prefix + "/section_view.html"
               })
        .state('column-default', {
                   parent: "layout",
                   controller: ColumnView,
                   templateUrl: partials_prefix + "/column_view.html"
               })
        .state('report-group-default', {
                   parent: "layout",
                   controller: ReportGroupView,
                   templateUrl: partials_prefix + "/reportgroup_view.html"
               })
        .state('report-default', {
                   parent: "layout",
                   controller: ReportEditView,
                   templateUrl: partials_prefix + "/report_edit.html"
               })
        .state('report-edit', {
                   parent: "layout",
                   controller: ReportEditView,
                   templateUrl: partials_prefix + "/report_addedit.html"
               })
        .state('report-group-addreport', {
                   parent: "layout",
                   controller: ReportAddView,
                   templateUrl: partials_prefix + "/report_addedit.html"
               })
        .state('column-addreport', {
                   parent: "layout",
                   controller: ReportAddView,
                   templateUrl: partials_prefix + "/report_addedit.html"
               })


});

app.filter('only_columns', function () {
    /* In section view, show the items that are columns */

    return function (input) {

        return input.filter(function (i) {
            return i.type == 'column';
        })

    }
});

app.directive('ngConfirmClick', [
    function () {
        return {
            priority: -1,
            restrict: 'A',
            link: function (scope, element, attrs) {
                element.bind('click', function (e) {
                    var message = attrs.ngConfirmClick;
                    if (message && !confirm(message)) {
                        e.stopImmediatePropagation();
                        e.preventDefault();
                    }
                });
            }
        }
    }
]);

var NOSPACES_REGEXP = /^[\S]*$/;
app.directive('nospaces', function () {
    return {
        require: 'ngModel',
        link: function (scope, elm, attrs, ctrl) {
            ctrl.$parsers.unshift(function (viewValue) {
                if (NOSPACES_REGEXP.test(viewValue)) {
                    // it is valid
                    ctrl.$setValidity('nospaces', true);
                    return viewValue;
                } else {
                    // it is invalid, return undefined (no model update)
                    ctrl.$setValidity('nospaces', false);
                    return undefined;
                }
            });
        }
    };
});