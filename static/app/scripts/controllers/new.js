'use strict';

/**
 * @ngdoc function
 * @name droneFrontendApp.controller:IndividualCtrl
 * @description
 * # IndividualCtrl
 * Controller of the droneFrontendApp
 */

angular.module('droneFrontendApp')
  .controller('NewCtrl', ['$scope', '$http','$interval','$location','droneService','ModalService',function ($scope,$http,$interval,$location,droneService,ModalService) {

    $scope.apiURL=droneService.apiURL;
    $scope.consoleRootURL=droneService.consoleRootURL;

  	console.log('Started New controller');
    $scope.connectionString="tcp:ip_address:port";
    $scope.connectionStringIP="ip_address";
    $scope.connectionStringPort="port";
    $scope.connectionStringType="tcp";
    $scope.vehicleName="drone name";
    $scope.lat=51.4049;
    $scope.lon=-1.3049;
    $scope.alt=105;
    $scope.dir=0;

  $scope.updateConnectionString=function(){
        $scope.connectionString=$scope.connectionStringType+":"+$scope.connectionStringIP+":"+$scope.connectionStringPort
  }

  $scope.$watch("connectionStringIP", function (newValue) {
    $scope.updateConnectionString()
  });
  $scope.$watch("connectionStringPort", function (newValue) {
    $scope.updateConnectionString()
  });
  $scope.$watch("connectionStringType", function (newValue) {
    $scope.updateConnectionString()
  });


	$scope.connectExisting = function() {
		console.log('Connect Existing Button Clicked');


    var payload={};
    payload['vehicle_type']="real";
    payload['name']=$scope.vehicleName;
    payload['connection_string']=$scope.connectionString;
    console.log('Sending POST with payload ',payload);

    $http.post($scope.apiURL + 'vehicle',payload,{headers : { 'Content-Type' : 'application/json; charset=UTF-8'  }}).then(function(data, status, headers, config) {
      console.log('API action POST success',data,status);
      $location.path($scope.consoleRootURL)
    },
    function(data, status, headers, config) {
      // log error
      console.log('API actions POST error',data, status, headers, config);
    });




	}
	$scope.createSimulated = function() {
		console.log('Create Simulated Button Clicked');
    droneService.droneName=$scope.vehicleName;
    droneService.lat=parseFloat($scope.lat);
    droneService.lon=parseFloat($scope.lon);
    droneService.alt=parseFloat($scope.alt);
    droneService.dir=parseFloat($scope.dir);

		$scope.showModal();


	}

 	$scope.showModal = function() {
        ModalService.showModal({
            templateUrl: 'views/modal.html',
            controller: "ModalCtrl"
        }).then(function(modal) {
            modal.element.modal();
            modal.close.then(function(result) {
                $scope.message = "You said " + result;
            });
        });
    }



  $scope.$on('$destroy', function() {
    // clean up stuff
      console.log('###################################################');
      console.log('Unloading New Controller');
  })




}]);

