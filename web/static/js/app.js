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
    $scope.input_write = true;
    //设置区域的折叠
    $scope.status = {
        isFirstOpen: true,
        isFirstDisabled: false,
        open: true
    };

    //表单与提交
    $scope.project = {};
    $scope.save_project = function () {
        var formData = $scope.project;
        formData['code'] = window._editor.getValue();//从全局变量_editor中获取code
        $http.post('/api/project/save', formData).success(function (data) {
            if (data.success) {
                $location.url('/project/edit/' + $scope.project.name);
                appAlert.add('success', data.msg, 3000);
            } else {
                appAlert.add('danger', data.msg, 5000);
            }
        });
    };
}]);

app.controller('projectEditCtrl', ['$scope', '$routeParams', '$http', '$rootScope', 'appAlert', 'appModal', function ($scope, $routeParams, $http, $rootScope, appAlert, appModal) {
    load_and_exec_CodeMirror();
    $scope.showTest = true;
    $scope.projectName = $routeParams.projectName;

    $scope.project = {};

    $http.get('/api/project/' + $scope.projectName).success(function (data) {
        $scope.project = data;
        document.getElementById('project_code_editor').value = data.code;
    });

    //表单与提交
    $scope.save_project = function () {
        var formData = $scope.project;
        formData['code'] = window._editor.getValue();//从全局变量_editor中获取code
        formData['edit'] = true; //标识为编辑计划
        $http.post('/api/project/save', formData).success(function (data) {
            if (data.success) {
                appAlert.add('success', data.msg, 3000);
            } else {
                appAlert.add('danger', data.msg, 5000);
            }
        });
    };

    var exec_test_first = true, url_record = [];
    $scope.exec_test = function (init_url, back) {
        var formData = {};

        //避免引用赋值
        formData['init_url'] = init_url ? init_url : $scope.project.init_url;
        formData['code'] = window._editor.getValue();//从全局变量_editor中获取code
        formData['edit'] = true; //标识为编辑计划

        //返回功能
        if (back) {
            formData['init_url'] = url_record.pop();
            if (formData['init_url'] == init_url) {
                formData['init_url'] = url_record.pop();
            }
            if (typeof formData['init_url'] === 'undefined') {
                formData['init_url'] = $scope.project.init_url;
            }
        }
        url_record.push(formData['init_url']);

        $http.post('/api/project/exec_test', formData).success(function (data) {
            if (data.success) {
                data.result['exec_test'] = $scope.exec_test;
                data.result['show_result_div'] = JSON.stringify(data.result.result) != '{}';
                $rootScope.execTestData = data.result;


                exec_test_first && appModal.open('测试', {}, 'component/exec-test', 'lg', false, function () {
                    exec_test_first = true;
                    url_record = [];
                });

                exec_test_first = false;

            } else {
                appAlert.add('danger', data.msg, 10000);
            }
        });
    };
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


app.factory('appModal', function ($rootScope, $modal) {
    return {
        open: function (title, params, template, size, sureFn, cancelFn) {
            var modalInstance = $modal.open({
                backdrop: false,
                animation: true,
                templateUrl: template ? template : 'myModalContent.html',
                controller: 'ModalInstanceCtrl',
                size: size,
                resolve: {
                    data: function () {
                        return {title: title, params: params, sureFn: sureFn, cancelFn: cancelFn};
                    }
                }
            });

            modalInstance.result.then(function (data) {
                sureFn && sureFn(data)
            }, function (data) {
                cancelFn && cancelFn(data)
            });
            modalInstance.rendered.then(function () {
                //拖拽
                var modal_head = document.getElementById('modal-header'),
                    modal = modal_head.parentNode.parentNode, left_fix = 0, top_fix = 0;

                modal_head.addEventListener('mousedown', mouseDown);
                function mouseDown(d_e) {
                    top_fix = parseInt(d_e.clientY - modal.offsetTop, 10);
                    left_fix = parseInt(d_e.clientX - modal.offsetLeft, 10);
                    document.addEventListener('mousemove', mouseMove);
                    document.addEventListener('mouseup', mouseUp);
                }

                function mouseMove(m_e) {
                    modal.style.marginLeft = m_e.clientX - left_fix + 'px';
                    modal.style.marginTop = m_e.clientY - top_fix + 'px';
                }

                function mouseUp() {
                    document.removeEventListener('mousemove', mouseMove);
                    document.removeEventListener('mouseup', mouseUp);
                }
            })
        }
    }
});

app.controller('ModalInstanceCtrl', function ($scope, $modalInstance, data) {

    $scope.title = data.title;
    $scope.params = data.params;

    $scope.ok = function () {
        $modalInstance.close();
    };
    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };
});

