'use strict';

var app = angular.module('PyFetch', ['ngRoute', 'angular-loading-bar']);

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
                controller: 'projectEditCtrl',
                resolve: {
                    depend: load_and_exec_CodeMirror
                }
            }).
            when('/project/add/new', {
                templateUrl: 'component/project-edit',
                controller: 'projectAddCtrl',
                resolve: {
                    depend: load_and_exec_CodeMirror
                }
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
    }])
;


app.controller('projectAddCtrl', ['$scope', '$routeParams', '$http', function ($scope, $routeParams, $http) {
    $scope.projectName = $routeParams.projectName;
    //$http.get('/api/project');
}]);

app.controller('projectEditCtrl', ['$scope', '$routeParams', '$http', function ($scope, $routeParams, $http) {
    $scope.projectName = $routeParams.projectName;
    //$http.get('/api/project');
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
    var load = function () {
        $http.get('/api/project').success(function (data) {
            $scope.projects = data;
        });
    };
    load();

    $scope.refresh = function () {
        load();
    };
});

app.controller('slaveCtrl', ['$scope', '$routeParams', '$http', function ($scope, $routeParams, $http) {
    var load = function () {
        $http.get('/api/slave').success(function (data) {
            $scope.slave = data;
        });
    };
    load();

    $scope.refresh = function () {
        load();
    };
}]);

app.controller('NavBarCtrl', function ($scope, $location) {
    $scope.isActive = function (route) {
        return $location.path().indexOf(route) === 0;
    }
});

function load_and_exec_CodeMirror($q) {
    var delay = $q.defer();

    $script(["/static/js/codemirror.js"], function () {// fixme 加载顺序缓存等等原因会导致在首页进入时有问题, 具体看console
        $script(['/static/js/codemirror-python.min.js'], function () {
            CodeMirror.fromTextArea(document.getElementById("project_code_editor"), {
                lineNumbers: true,
                //showCursorWhenSelecting: true,
                //value: 'gdgdfg',
                //lineWrapping: true,
                //styleActiveLine: true,
                //autofocus: true,
                //matchBrackets: true,
                mode: "python"
            });
            return delay.promise;
        });
    });
}