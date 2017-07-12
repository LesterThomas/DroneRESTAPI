'use strict';

/**
 * @ngdoc overview
 * @name droneFrontendApp
 * @description
 * # droneFrontendApp
 *
 * Main module of the application.
 */
angular
  .module('droneFrontendApp', [
    'ngAnimate',
    'ngCookies',
    'ngResource',
    'ngRoute',
    'ngSanitize',
    'ngTouch',
	'ngMap',
	'chart.js',
  'angularModalService'
  ])
  .config(function ($routeProvider) {
    $routeProvider
      .when('/individual', {
        templateUrl: 'views/individual.html',
        controller: 'IndividualCtrl',
        controllerAs: 'individual'
      })
      .when('/new', {
        templateUrl: 'views/new.html',
        controller: 'NewCtrl',
        controllerAs: 'new'
      })
      .when('/', {
        templateUrl: 'views/main.html',
        controller: 'MainCtrl',
        controllerAs: 'main'
      })
      .when('/modal', {
        templateUrl: 'views/modal.html',
        controller: 'ModalCtrl',
        controllerAs: 'modal'
      })
      .when('/perf', {
        templateUrl: 'views/performance.html',
        controller: 'PerformanceCtrl',
        controllerAs: 'Performance'
      })
      .otherwise({
        redirectTo: '/'
      });
  });
