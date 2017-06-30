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
  	$scope.apiURL=individualDrone.apiURL;
	$scope.drones=[];
	$scope.markers=[];
	$scope.zones=[];

	var intervalTimer = $interval(updateDrones, 250);
	updateDrones();
	function updateDrones() {
			$http.get($scope.apiURL + 'vehicle?details=true').
			    then(function(data, status, headers, config) {
						console.log('API get success',data,status);	
						$scope.drones=data.data._embedded.vehicle;

						for ( var droneId in $scope.drones){
							//manipulate the model
							var drone=$scope.drones[droneId];
							console.log('Drone:',drone);	
							if (drone.vehicleStatus.armed==true) {
								drone.vehicleStatus.armed_status="ARMED";
								drone.vehicleStatus.armed_colour={color:'red'};
							} else {
								drone.vehicleStatus.armed_status="DISARMED";
								drone.vehicleStatus.armed_colour={color:'green'};
							}
							if (drone.vehicleStatus.last_heartbeat<1) {
								drone.vehicleStatus.heartbeat_status="OK";
								drone.vehicleStatus.heartbeat_colour={color:'green'};
							} else {
								drone.vehicleStatus.heartbeat_status="Last Heartbeat " + Math.round(drone.vehicleStatus.last_heartbeat) + " s";
								drone.vehicleStatus.heartbeat_colour={color:'red'};
							}
							if (drone.vehicleStatus.ekf_ok==true) {
								drone.vehicleStatus.ekf_status="OK";
								drone.vehicleStatus.ekf_colour={color:'green'};
							} else {
								drone.vehicleStatus.ekf_status="EFK ERROR";
								drone.vehicleStatus.ekf_colour={color:'red'};
							}
							drone.vehicleStatus.distance_home= Math.sqrt((drone.vehicleStatus.local_frame.east)*(drone.vehicleStatus.local_frame.east)+(drone.vehicleStatus.local_frame.north)*(drone.vehicleStatus.local_frame.north));   
						}
					
	                    NgMap.getMap().then(function(map) {
								
	                        var bounds=new google.maps.LatLngBounds();

	                        for(var droneIndex in $scope.drones) {
	                        	bounds=bounds.extend({lat:$scope.drones[droneIndex].vehicleStatus.global_frame.lat,lng:$scope.drones[droneIndex].vehicleStatus.global_frame.lon});
	                        }


							for(var droneIndex in $scope.drones) {

								//draw drones (markers)
								if ($scope.markers[droneIndex]) {
							        //console.log('Marker already exists');
						        } else
		        				{
							        $scope.markers[droneIndex] = new google.maps.Marker({ title: "Drone: " + $scope.drones[droneIndex].vehicleStatus.id, icon: 
									{ path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,scale: 6, fillColor: 'yellow', fillOpacity: 0.8, strokeColor: 'red', strokeWeight: 1, rotation:$scope.drones[droneIndex].vehicleStatus.heading} 
								    });
							        //map.setCenter(new google.maps.LatLng(avgLat, avgLon ) ); //Set map based on avg  Drone location
							        map.fitBounds(bounds);
							        $scope.markers[droneIndex].setMap(map);
						        }

						        //if heading has changed, recreate icon
						        if ($scope.markers[droneIndex].icon.rotation != $scope.drones[droneIndex].vehicleStatus.heading) {
							        $scope.markers[droneIndex].setMap(null);
							        $scope.markers[droneIndex] = new google.maps.Marker({ title: "Drone: " + $scope.drones[droneIndex].vehicleStatus.id, icon: 
									        { path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,scale: 6, fillColor: 'yellow', fillOpacity: 0.8, strokeColor: 'red', strokeWeight: 1, rotation:$scope.drones[droneIndex].vehicleStatus.heading} 
								        })
							        $scope.markers[droneIndex].setMap(map);
						        }
						        $scope.markers[droneIndex].setPosition(new google.maps.LatLng($scope.drones[droneIndex].vehicleStatus.global_frame.lat, $scope.drones[droneIndex].vehicleStatus.global_frame.lon));

						        //draw authorized fly zones
								if ($scope.zones[droneIndex]) {
							        //console.log('Zone already exists');
						        } else
		        				{
		        					if ($scope.drones[droneIndex].vehicleStatus.zone.shape) {
			        					var center={lat:$scope.drones[droneIndex].vehicleStatus.zone.shape.lat,lng:$scope.drones[droneIndex].vehicleStatus.zone.shape.lon};
								        $scope.zones[droneIndex] = new google.maps.Circle({strokeColor:'#22FF22', strokeOpacity:0.8,fillColor:'#00FF00',fillOpacity:0.10,center:center ,radius: $scope.drones[droneIndex].vehicleStatus.zone.shape.radius,map:map}); 
								    }
								}

						    }
						});
	                          
					},
					function(data, status, headers, config) {
					  // log error
						console.log('API get error',data, status, headers, config);
					});

		}


		$scope.selectIndividual=function(inDrone) {
			console.log('Selected drone',inDrone);
			individualDrone.droneId=inDrone.id;
			$location.path('/individual')

		}


		$scope.$on('$destroy', function() {
		  // clean up stuff
		  	console.log('###################################################'); 
		  	console.log('Unloading Main Controller'); 
			$interval.cancel(intervalTimer);
			individualDrone.apiURL=$scope.apiURL;

			for(var droneIndex in $scope.markers) {

			    $scope.markers[droneIndex].setMap(null);
			}
			$scope.markers.splice(0, $scope.markers.length);
		

		})			

	}]);

