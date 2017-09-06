'use strict';

/**
 * @ngdoc function
 * @name droneFrontendApp.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the droneFrontendApp
 */

angular.module('droneFrontendApp')
  .controller('MainCtrl', ['$scope','$rootScope', '$location','$interval','$http','facebookUser','droneService',function ($scope,$rootScope,$location,$interval,$http,facebookUser,droneService) {

  	console.log('Started Main controller');
    $scope.apiURL=droneService.apiURL;

    $rootScope.$on('fbLoginSuccess', function(name, response) {
      facebookUser.then(function(user) {
        user.api('/me',{fields:['name','email']}).then(function(response) {
            $rootScope.loggedInUser = response;

            //add to droneAPIServer user database to get API Key
            var payload={"name":response.name,"email":response.email,"id":response.id,"id_provider":"Facebook"};
            $http.post($scope.apiURL + 'user',payload,{
                headers : {
                    'Content-Type' : 'application/json; charset=UTF-8'
                }
            })
            .then(function(data, status, headers, config) {
                    var api_key=data.data.api_key;
                    $rootScope.loggedInUser.api_key=api_key;
                    console.log('API  user POST success',data,status);

                },
                function(data, status, headers, config) {
                    // log error
                    console.log('API user POST error',data, status, headers, config);
                });


        });
      });
    });

    $rootScope.$on('fbLogoutSuccess', function() {
      $scope.$apply(function() {
        $rootScope.loggedInUser = {};
      });
    });

	}]);

