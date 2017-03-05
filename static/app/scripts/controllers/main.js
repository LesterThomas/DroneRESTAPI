'use strict';

/**
 * @ngdoc function
 * @name droneFrontendApp.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the droneFrontendApp
 */
   
angular.module('droneFrontendApp')
  .controller('MainCtrl', ['$scope', '$http','NgMap','$interval','$location','individualDrone',function ($scope,$http,NgMap,$interval,$location,individualDrone) {
	  
  	console.log('Started Main controller'); 
  	$scope.apiURL='http://localhost:1235/'; //http://sail.vodafone.com/drone/';
  	$scope.droneIndex=0;
	$scope.drones=[];
	$scope.droneDetails=[];
	var intervalTimer = $interval(updateDrones, 2000);
	function updateDrones() {
		$http.get($scope.apiURL + 'vehicle').
		    then(function(data, status, headers, config) {
					console.log('API get success',data,status);	
					$scope.drones=data.data;
					
				},
				function(data, status, headers, config) {
				  // log error
					console.log('API get error',data, status, headers, config);
				});
			
		if ($scope.drones.length>0) {
			if ($scope.droneIndex>=$scope.drones.length) {
				$scope.droneIndex=0;
				}
			console.log('Get detailed status for drone ' + $scope.droneIndex);
			$http.get($scope.apiURL + 'vehicle/'+$scope.drones[$scope.droneIndex].id+'/').
			    then(function(data, status, headers, config) {
						console.log('API get success',data,status);	
						var vehicleStatus=data.data.vehicleStatus;
						//manipulate the model
						if (vehicleStatus.armed==true) {
							vehicleStatus.armed_status="ARMED";
							vehicleStatus.armed_colour={color:'red'};
						} else {
							vehicleStatus.armed_status="DISARMED";
							vehicleStatus.armed_colour={color:'green'};
						}
						if (vehicleStatus.last_heartbeat<1) {
							vehicleStatus.heartbeat_status="OK";
							vehicleStatus.heartbeat_colour={color:'green'};
						} else {
							vehicleStatus.heartbeat_status="Last Heartbeat " + Math.round(vehicleStatus.last_heartbeat) + " s";
							vehicleStatus.heartbeat_colour={color:'red'};
						}
						if (vehicleStatus.ekf_ok==true) {
							vehicleStatus.ekf_status="OK";
							vehicleStatus.ekf_colour={color:'green'};
						} else {
							vehicleStatus.ekf_status="EFK ERROR";
							vehicleStatus.ekf_colour={color:'red'};
						}
						vehicleStatus.distance_home= Math.sqrt((vehicleStatus.local_frame.east)*(vehicleStatus.local_frame.east)+(vehicleStatus.local_frame.north)*(vehicleStatus.local_frame.north));                             
						//put the vehicle status in the array at the correct index;
						var droneIndex=-1;
						for (var i in $scope.drones){
							if ($scope.drones[i].id==vehicleStatus.id){
								droneIndex=i;
							}
						}
						if (droneIndex==-1){
							console.warn("No drone found with ID"+vehicleStatus.id);
						} else {
							$scope.droneDetails[droneIndex]=vehicleStatus;
						}
					

					},
					function(data, status, headers, config) {
					  // log error
						console.log('API get error',data, status, headers, config);
					});



			$scope.droneIndex++;			
			}
		}


		$scope.selectIndividual=function(inDrone) {
			console.log('Selected drone',inDrone);
			individualDrone.droneId=inDrone.id;
			$location.path('/individual')

		}

	}]);

