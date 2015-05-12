'use strict';

var app = angular.module('PyFetch', ['ngRoute', 'angular-loading-bar', 'ui.bootstrap']);

app.config(['$routeProvider', '$locationProvider', 'cfpLoadingBarProvider', '$httpProvider',
    function ($routeProvider, $locationProvider, cfpLoadingBarProvider, $httpProvider) {
        if (!$httpProvider.defaults.headers.get) {
            $httpProvider.defaults.headers.get = {};
        }
        $httpProvider.defaults.headers.common["X-Requested-With"] = 'XMLHttpRequest';
        $httpProvider.defaults.headers.get['Cache-Control'] = 'no-cache';
        $httpProvider.defaults.headers.get['Pragma'] = 'no-cache';
        $locationProvider.html5Mode(true);
        cfpLoadingBarProvider.includeSpinner = false;
        $routeProvider.
            when('/project/edit/:projectName', {
                templateUrl: 'component/project-edit',
                controller: 'projectEditCtrl'
            }).
            when('/project/add/new', {
                templateUrl: 'component/project-edit',
                controller: 'projectAddCtrl'
            }).
            when('/project', {
                templateUrl: 'component/project',
                controller: 'projectCtrl'
            }).
            when('/slave', {
                templateUrl: 'component/slave',
                controller: 'slaveCtrl'
            }).
            when('/slave/task/:ip', {
                templateUrl: 'component/task',
                controller: 'slaveTaskCtrl'
            }).
            when('/project/result/:projectName', {
                templateUrl: 'component/result',
                controller: 'projectResultCtrl'
            }).
            when('/project/task/:projectName', {
                templateUrl: 'component/task',
                controller: 'projectTaskCtrl'
            }).
            otherwise({
                redirectTo: '/project'
            });
    }]);


app.controller('projectAddCtrl', ['$scope', '$rootScope', '$http', '$location', 'appAlert', function ($scope, $rootScope, $http, $location, appAlert) {
    load_and_exec_CodeMirror();

    //设置区域的折叠
    $scope.status = {
        isFirstOpen: true,
        isFirstDisabled: false,
        open: true
    };

    //表单与提交
    $scope.project = {};
    $scope.exec_test = function () {
        var formData = $scope.project;
        formData['code'] = window._editor.getValue();//从全局变量_editor中获取code
        $http.post('/api/project/add', formData).success(function (data) {
            if (data.success) {
                $location.url('/project/edit/' + $scope.project.name);
                appAlert.add('success', data.msg, 3000);
            } else {
                appAlert.add('danger', data.msg, 5000);
            }
        });
    };
}]);

app.controller('projectEditCtrl', ['$scope', '$routeParams', '$http', function ($scope, $routeParams, $http) {
    load_and_exec_CodeMirror();
    $scope.showTest = true;
    $scope.projectName = $routeParams.projectName;

    $http.get('/api/project/' + $scope.projectName).success(function (data) {
        $scope.project = data;
        document.getElementById('project_code_editor').value = data.code;
    });
}]);

app.controller('projectResultCtrl', ['$scope', '$http', '$routeParams', function ($scope, $http, $routeParams) {
    $http.get('/api/result/' + $routeParams.projectName).success(function (data) {
        $scope.th_title = [];
        for (var key in data[0]) {
            $scope.th_title.push(key);
        }
        $scope.results = data;
    });
}]);

app.controller('slaveTaskCtrl', ['$scope', '$http', '$routeParams', function ($scope, $http, $routeParams) {
    $http.get('/api/slave/' + $routeParams.ip).success(function (data) {
        $scope.tasks = data;
    });
}]);

app.controller('projectTaskCtrl', ['$scope', '$http', '$routeParams', function ($scope, $http, $routeParams) {
    $http.get('/api/task/' + $routeParams.projectName).success(function (data) {
        $scope.tasks = data;
    });
}]);

app.controller('projectCtrl', function ($scope, $http) {
    var load = function (manual) {
        manual && ($scope.show_load_icon = true);

        $http.get('/api/project').success(function (data) {
            setTimeout(function () {
                $scope.show_load_icon = false;
            }, 1);
            $scope.projects = data;
        });
    };
    load(false);

    $scope.refresh = function () {
        load(true);
    };
});

app.controller('slaveCtrl', ['$scope', '$routeParams', '$http', function ($scope, $routeParams, $http) {
    var load = function (manual) {
        manual && ($scope.show_load_icon = true);

        $http.get('/api/slave').success(function (data) {
            setTimeout(function () {
                $scope.show_load_icon = false;
            }, 1);
            $scope.slave = data;
        });
    };
    load(false);

    $scope.refresh = function () {
        load(true);
    };
}]);

app.controller('NavBarCtrl', function ($scope, $location) {
    $scope.isActive = function (route) {
        return $location.path().indexOf(route) === 0;
    }
});

app.controller('scrollToTop', function ($scope) {
    $scope.toTop = function () {
        document.body.scrollTop && (document.body.scrollTop = 0);
        document.documentElement.scrollTop && (document.documentElement.scrollTop = 0);
    }
});

app.factory('appAlert', [
    '$rootScope', '$timeout', '$sce', function ($rootScope, $timeout, $sce) {
        var alertService;
        $rootScope.alerts = [];
        return alertService = {
            add: function (type, msg, timeout) {
                $rootScope.alerts.push({
                    type: type,
                    msg: $sce.trustAsHtml(msg),
                    close: function () {
                        return alertService.closeAlert(this);
                    }
                });

                if (timeout) {
                    $timeout(function () {
                        alertService.closeAlert(this);
                    }, timeout);
                }
            },
            closeAlert: function (alert) {
                return this.closeAlertIdx($rootScope.alerts.indexOf(alert));
            },
            closeAlertIdx: function (index) {
                return $rootScope.alerts.splice(index, 1);
            },
            clear: function () {
                $rootScope.alerts = [];
            }
        };
    }
]);
function load_and_exec_CodeMirror(defaultValue) {
    $script(["/static/js/codemirror.js"], function () {
        $script(["/static/js/codemirror-component.min.js"], function () {
            window._editor = CodeMirror.fromTextArea(document.getElementById("project_code_editor"), {
                lineNumbers: true,
                styleActiveLine: true,
                autofocus: true,
                tabSize: 4
            });

            defaultValue && window._editor.setValue(defaultValue)
        });
    });
}
