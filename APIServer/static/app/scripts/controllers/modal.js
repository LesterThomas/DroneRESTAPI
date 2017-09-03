'use strict';

/**
 * @ngdoc function
 * @name droneFrontendApp.controller:IndividualCtrl
 * @description
 * # IndividualCtrl
 * Controller of the droneFrontendApp
 */

angular.module('droneFrontendApp')
  .controller('ModalCtrl', ['$scope','$http','$interval','$location','droneService',function ($scope, $http, $interval, $location,droneService,close) {


  	console.log('Started modal controller');
    $scope.apiURL=droneService.apiURL;
    $scope.consoleRootURL=droneService.consoleRootURL;

	$scope.progress=[false,false,false,false,false,false,false]
	$scope.progressClass=['alert-warning','','','','','','']
	$scope.progressMessage=['Connecting to Cloud Service']
	$scope.progressIndex=0;
	$scope.progressFinished=false;
	$scope.intervalTimer=null;

	var payload={};
	payload['vehicle_type']="simulated";
	payload['name']=droneService.droneName;
    payload['lat']=droneService.lat;
    payload['lon']=droneService.lon;
    payload['alt']=droneService.alt;
    payload['dir']=droneService.dir;

	console.log('Sending POST with payload ',payload);

	$http.post($scope.apiURL + 'vehicle',payload,{headers : { 'Content-Type' : 'application/json; charset=UTF-8'  }}).then(function(data, status, headers, config) {
		console.log('API action POST success',data,status);
		$scope.progress[0]=true;
		$scope.progressClass[0]='alert-success';
		$scope.progressClass[1]='alert-warning';
		$scope.intervalTimer = $interval(updateProgress, 2000);

	},
	function(data, status, headers, config) {
	  // log error
		console.log('API actions POST error',data, status, headers, config);
		$scope.progressMessage[0]='Error connecting to Cloud Service';
		$scope.progressClass[0]='alert-error';
	});





	function updateProgress() {
		$scope.progress[$scope.progressIndex]=true;
		$scope.progressClass[$scope.progressIndex]='alert-success';
		$scope.progressClass[$scope.progressIndex+1]='alert-warning';
		$scope.progressIndex++;
		if ($scope.progressIndex==4){
			$scope.progressFinished=true;
			$interval.cancel($scope.intervalTimer);
		}
	}

	 $scope.close = function(result) {
	 	//close(result, 500); // close, but give 500ms for bootstrap to animate
	 };


	$scope.backHome=function() {
		console.log('backHome button pressed');
 		$scope.close('finished'); // close, but give 500ms for bootstrap to animate
		window.location=$scope.consoleRootURL;

	}

}]);

