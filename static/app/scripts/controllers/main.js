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
  	$scope.droneIndex=0;
	$scope.drones=[];
	$scope.droneDetails=[];
	$scope.markers=[];
	$scope.zones=[];

	var intervalTimer = $interval(updateDrones, 500);
	updateDrones();
	function updateDrones() {
		if ($scope.droneIndex<2) {
			$http.get($scope.apiURL + 'vehicle').
			    then(function(data, status, headers, config) {
						console.log('API get success',data,status);	
						$scope.drones=data.data._embedded.vehicle;
						
					},
					function(data, status, headers, config) {
					  // log error
						console.log('API get error',data, status, headers, config);
					});
			}
		if ($scope.drones.length>0) {
			if ($scope.droneIndex>=$scope.drones.length) {
				$scope.droneIndex=0;
				}
			console.log('Get detailed status for drone ' + $scope.droneIndex);
			$http.get($scope.apiURL + 'vehicle/'+$scope.drones[$scope.droneIndex].id).
			    then(function(data, status, headers, config) {
						console.log('API get success',data,status);	
						var vehicleStatus=data.data;
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
					



                    NgMap.getMap().then(function(map) {
							
                        var bounds=new google.maps.LatLngBounds();

                        for(var droneIndex in $scope.droneDetails) {
                        	bounds=bounds.extend({lat:$scope.droneDetails[droneIndex].global_frame.lat,lng:$scope.droneDetails[droneIndex].global_frame.lon});
                        }


						for(var droneIndex in $scope.droneDetails) {

							//draw drones (markers)
							if ($scope.markers[droneIndex]) {
						        //console.log('Marker already exists');
					        } else
	        				{
						        $scope.markers[droneIndex] = new google.maps.Marker({ title: "Drone: " + $scope.droneDetails[droneIndex].id, icon: 
								{ path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,scale: 6, fillColor: 'yellow', fillOpacity: 0.8, strokeColor: 'red', strokeWeight: 1, rotation:$scope.droneDetails[droneIndex].heading} 
							    });
						        //map.setCenter(new google.maps.LatLng(avgLat, avgLon ) ); //Set map based on avg  Drone location
						        map.fitBounds(bounds);
						        $scope.markers[droneIndex].setMap(map);
					        }

					        //if heading has changed, recreate icon
					        if ($scope.markers[droneIndex].icon.rotation != $scope.droneDetails[droneIndex].heading) {
						        $scope.markers[droneIndex].setMap(null);
						        $scope.markers[droneIndex] = new google.maps.Marker({ title: "Drone: " + $scope.droneDetails[droneIndex].id, icon: 
								        { path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,scale: 6, fillColor: 'yellow', fillOpacity: 0.8, strokeColor: 'red', strokeWeight: 1, rotation:$scope.droneDetails[droneIndex].heading} 
							        })
						        $scope.markers[droneIndex].setMap(map);
					        }
					        $scope.markers[droneIndex].setPosition(new google.maps.LatLng($scope.droneDetails[droneIndex].global_frame.lat, $scope.droneDetails[droneIndex].global_frame.lon));

					        //draw authorized fly zones
							if ($scope.zones[droneIndex]) {
						        //console.log('Zone already exists');
					        } else
	        				{
	        					if ($scope.droneDetails[droneIndex].zone.shape) {
		        					var center={lat:$scope.droneDetails[droneIndex].zone.shape.lat,lng:$scope.droneDetails[droneIndex].zone.shape.lon};
							        $scope.zones[droneIndex] = new google.maps.Circle({strokeColor:'#22FF22', strokeOpacity:0.8,fillColor:'#00FF00',fillOpacity:0.10,center:center ,radius: $scope.droneDetails[droneIndex].zone.shape.radius,map:map}); 
							    }
							}

					    }
					});
                          

//{"zone":{"shape":{"name":"circle","radius":500}}}


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

