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
	'chart.js'
  ])
  .config(function ($routeProvider) {
    $routeProvider
      .when('/', {
        templateUrl: 'views/main.html',
        controller: 'MainCtrl',
        controllerAs: 'main'
      })

      .otherwise({
        redirectTo: '/'
      });
  });
