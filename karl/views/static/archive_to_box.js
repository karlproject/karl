/*

 Used by the Archive to Box admin application. This is an
 AngularJS app.

 */

function ArchiveToBoxController (Restangular, $modal, $http) {
    var _this = this;

    this.inactiveCommunities = null;
    this.isLoading = function () {
        return this.inactiveCommunities === null;
    };

    var baseInactives = Restangular.all('arc2box/communities');

    // Handle filters
    this.lastActivity = 900;
    this.limit = 20;
    this.filterText = null;
    this.reload = function () {
        _this.isSubmitting = true;
        // User clicked the "Over 18 months" checkbox or the search box
        var params = {};
        // Only send query string parameters if they are not null
        if (this.lastActivity || this.lastActivity === 0) {
            params.last_activity = this.lastActivity;
        }
        if (this.limit) {
            params.limit = this.limit;
        }
        if (this.filterText) {
            params.filter = this.filterText;
        }

        baseInactives.getList(params)
            .then(
                function (success) {
                    _this.isSubmitting = false;
                    _this.inactiveCommunities = success;
                },
                function (failure) {
                    console.debug('failure', failure);
                }
            );
    };

    this.clearExceptions = function () {
        console.log('clickded clear exceptions');
        var url = '/arc2box/clear_exceptions';
        $http.post(url)
            .success(
                function () {
                    console.debug('clear exceptions');
                    _this.reload();
                })
            .error(
                function (error) {
                    console.debug('clear exceptions error', error);
                }
            );
        return false;
    };

    // Let's go ahead and load this the first time
    this.reload();

    this.setStatus = function (target, action) {
        var url = '/arc2box/communities/' + target.name;
        $http.patch(url, {action: action})
            .success(
                function () {
                    console.debug('success setting ' + target.name + ' to ' + action);
                    _this.reload();
                })
            .error(
                function (error) {
                    console.debug('error', error);
                }
            )
    };


    this.showLog = function (target) {
        var modalInstance = $modal.open(
            {
                templateUrl: 'myModalContent.html',
                controller: ModalController,
                controllerAs: 'ctrl',
                size: 'lg',
                resolve: {
                    target: function () {
                        return target;
                    }
                }
            });
    }
}

var app = angular.module(
    'archiveToBox',
    ['restangular', 'ui.bootstrap'
    ]);

app.controller('ArchiveToBoxController', ArchiveToBoxController);