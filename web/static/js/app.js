'use strict';

var app = angular.module('PyFetch', ['ngRoute', 'angular-loading-bar']);

app.config(['$routeProvider', '$locationProvider', 'cfpLoadingBarProvider',
    function ($routeProvider, $locationProvider, cfpLoadingBarProvider) {
        $locationProvider.html5Mode(true);
        cfpLoadingBarProvider.includeSpinner = false;
        $routeProvider.
            when('/', {
                templateUrl: 'component/index',
                controller: 'indexCtrl'
            }).
            when('/project/:projectName', {
                templateUrl: 'component/project',
                controller: 'projectEditCtrl'
            }).
            when('/slave', {
                templateUrl: 'component/slave',
                controller: 'slaveCtrl'
            }).
            when('/slave/task/:slaveName', {
                templateUrl: 'component/task',
                controller: 'slaveTaskCtrl'
            }).
            when('/slave/result/:projectName', {
                templateUrl: 'component/result',
                controller: 'slaveResultCtrl'
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
                redirectTo: '/'
            });
    }]);


app.controller('projectEditCtrl', ['$scope', '$routeParams', '$http', function ($scope, $routeParams, $http) {
    $scope.projectName = $routeParams.projectName;
    $http.get('/api/project');
}]);

app.controller('slaveResultCtrl', ['$scope', '$http', '$routeParams', function ($scope, $http, $routeParams) {
    $http.get('/api/test');
    console.log($routeParams);
}]);
app.controller('projectResultCtrl', ['$scope', '$http', '$routeParams', function ($scope, $http, $routeParams) {
    $http.get('/api/result/' + $routeParams.projectName).success(function (data) {

        $scope.th_title = []
        for (var key in data[0]) {
            $scope.th_title.push(key)
        }

        console.log($scope.th_title);
        $scope.results = data;
    });
}]);

app.controller('slaveTaskCtrl', ['$scope', '$http', '$routeParams', function ($scope, $http, $routeParams) {
    $http.get('/api/test');
    console.log($routeParams);
}]);

app.controller('projectTaskCtrl', ['$scope', '$http', '$routeParams', function ($scope, $http, $routeParams) {
    $http.get('/api/task/' + $routeParams.projectName).success(function (data) {
        $scope.tasks = data;
    });
}]);

app.controller('indexCtrl', function ($scope, $http) {
    $http.get('/api/project').success(function (data) {
        $scope.projects = data
    });
});

app.controller('slaveCtrl', ['$scope', '$routeParams', '$http', function ($scope, $routeParams, $http) {
    $http.get('/api/test');
}]);

app.controller('NavBarCtrl', function ($scope, $location) {
    $scope.isActive = function (route) {
        return route === $location.path();
    }
});