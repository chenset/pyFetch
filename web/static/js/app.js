var app = angular.module('PyFetch', ['ngRoute']);

app.config(['$routeProvider','$locationProvider',
    function ($routeProvider, $locationProvider) {
        $locationProvider.html5Mode(true);

        $routeProvider.
            when('/index', {
                templateUrl: 'index.html',
                controller: 'indexCtrl'
            }).
            when('/project/:projectName', {
                templateUrl: 'project',
                controller: 'projectCtrl'
            }).
            otherwise({
                redirectTo: '/'
            });
    }]);

app.controller('projectCtrl', function ($scope) {
    $scope.phones = [
        {
            'name': 'Nexus S',
            'snippet': 'Fast just got faster with Nexus S.'
        },
        {
            'name': 'Motorola XOOM™ with Wi-Fi',
            'snippet': 'The Next, Next Generation tablet.'
        },
        {
            'name': 'MOTOROLA XOOM™',
            'snippet': 'The Next, Next Generation tablet.'
        }
    ];
});

app.controller('indexCtrl', function ($scope) {
    $scope.phones = [
        {
            'name': 'Nexus S',
            'snippet': 'Fast just got faster with Nexus S.'
        },
        {
            'name': 'Motorola XOOM™ with Wi-Fi',
            'snippet': 'The Next, Next Generation tablet.'
        },
        {
            'name': 'MOTOROLA XOOM™',
            'snippet': 'The Next, Next Generation tablet.'
        }
    ];
});