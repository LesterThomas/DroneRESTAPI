'use strict';

/**
 * @ngdoc function
 * @name droneFrontendApp.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the droneFrontendApp
 */
   
angular.module('droneFrontendApp')
  .controller('MainCtrl', ['$scope', '$http','NgMap','$interval',function ($scope,$http,NgMap,$interval) {
	  
  	console.log('Started controller'); 
	$scope.status='Loading';
	$scope.vehicleStatus={};
	$scope.markers=[];
	console.log('Calling API'); 
	var intervalTimer = $interval(updateDrone, 1000);
	function updateDrone() {
		$http.get('http://sail.vodafone.com/drone/vehicle/1/').
		    then(function(data, status, headers, config) {
					console.log('API get success',data,status);	
					$scope.vehicleStatus=data.data.vehicleStatus;
					$scope.vehicleStatus.altitude=-$scope.vehicleStatus.local_frame.down;
					NgMap.getMap().then(function(map) {
					if ($scope.markers.length>0) {
						console.log('Marker already exists');
					} else
					{
						$scope.markers[0] = new google.maps.Marker({ title: "Drone: " + 1 });
						map.setCenter(new google.maps.LatLng( $scope.vehicleStatus.global_frame.lat, $scope.vehicleStatus.global_frame.lon ) );
						$scope.markers[0].setMap(map);

					}
					$scope.markers[0].setPosition(new google.maps.LatLng($scope.vehicleStatus.global_frame.lat, $scope.vehicleStatus.global_frame.lon));
						
					console.log(map.getCenter());
					console.log('markers', map.markers);
					console.log('shapes', map.shapes);
				  });				
					
				},
				function(data, status, headers, config) {
				  // log error
					console.log('API get error',data, status, headers, config);
				});
			}
	console.log('Finished calling API'); 
	


  

  }]);
