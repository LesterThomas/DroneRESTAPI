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
	'ngVis',
    'ngAnimate',
    'ngCookies',
    'ngResource',
    'ngRoute',
    'ngSanitize',
    'ngTouch',
	'ngMap',
	'chart.js',
    'angularModalService',
    'facebookUtils'
  ])
  .config(function ($routeProvider) {
    $routeProvider
      .when('/individual', {
        templateUrl: 'views/individual.html',
        controller: 'IndividualCtrl',
        controllerAs: 'individual',
        needAuth:true
      })
      .when('/new', {
        templateUrl: 'views/new.html',
        controller: 'NewCtrl',
        controllerAs: 'new',
        needAuth:true
      })
      .when('/inventory', {
        templateUrl: 'views/inventory.html',
        controller: 'InventoryCtrl',
        controllerAs: 'new',
        needAuth:true
      })
      .when('/', {
        templateUrl: 'views/main.html',
        controller: 'MainCtrl',
        controllerAs: 'main'
      })
      .when('/network', {
        templateUrl: 'views/network.html',
        controller: 'NetworkCtrl',
        controllerAs: 'modal',
        needAuth:true
      })
      .when('/perf', {
        templateUrl: 'views/performance.html',
        controller: 'PerformanceCtrl',
        controllerAs: 'Performance',
        needAuth:true
      })
      .otherwise({
        redirectTo: '/'
      });
  })
  .constant('facebookConfigSettings', {
    'appID' : '136908103594406',
    'routingEnabled':true
});
