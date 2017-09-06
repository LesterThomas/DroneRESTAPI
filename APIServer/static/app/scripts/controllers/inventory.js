'use strict';

/**
 * @ngdoc function
 * @name droneFrontendApp.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the droneFrontendApp
 */

angular.module('droneFrontendApp')
  .controller('InventoryCtrl', ['$scope', 'NgMap','$location','$interval','droneService',function ($scope,NgMap,$location,$interval,droneService) {

  	console.log('Started Main controller');
  	$scope.apiURL=droneService.apiURL;
	$scope.drones=droneService.drones;
	$scope.markers=[];
	$scope.zones=[];

	$scope.mappedAdvisories=[];
	$scope.advisories=droneService.advisories;
	$scope.advisoriesCount=0;


	var mapIntervalTimer = $interval(updateMap, 250);
	var deleteMarketsTimer = $interval(deleteAllMarkers, 5000);
	var deleteZonesTimer = $interval(deleteAllZones, 7000);
	var deleteAdvisoriesTimer = $interval(deleteAllAdvisories, 7000);
	updateMap();
	function updateMap() {
        NgMap.getMap().then(function(map) {
			//console.log('Main Map',map);

            var bounds=new google.maps.LatLngBounds();

            for(var droneIndex in $scope.drones.collection) {
            	if ($scope.drones.collection[droneIndex].vehicle_status){
	            	bounds=bounds.extend({lat:$scope.drones.collection[droneIndex].vehicle_status.global_frame.lat+0.003,lng:$scope.drones.collection[droneIndex].vehicle_status.global_frame.lon+0.003});
	            	bounds=bounds.extend({lat:$scope.drones.collection[droneIndex].vehicle_status.global_frame.lat-0.003,lng:$scope.drones.collection[droneIndex].vehicle_status.global_frame.lon-0.003});
	            }
            }


			for(var droneIndex in $scope.drones.collection) {

				//draw drones (markers)
				if ($scope.markers[droneIndex]) {
			        //console.log('Marker already exists');
		        } else
				{
			        $scope.markers[droneIndex] = new google.maps.Marker({ title: "Drone: " + $scope.drones.collection[droneIndex].id, icon:
					{ path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,scale: 6, fillColor: 'yellow', fillOpacity: 0.8, strokeColor: 'red', strokeWeight: 1, rotation:$scope.drones.collection[droneIndex].vehicle_status.heading}
				    });
			        //map.setCenter(new google.maps.LatLng(avgLat, avgLon ) ); //Set map based on avg  Drone location
			        map.fitBounds(bounds);
			        $scope.markers[droneIndex].setMap(map);
		        }

		        //if heading has changed, recreate icon
		        if ($scope.markers[droneIndex].icon.rotation != $scope.drones.collection[droneIndex].vehicle_status.heading) {
			        $scope.markers[droneIndex].setMap(null);
			        $scope.markers[droneIndex] = new google.maps.Marker({ title: "Drone: " + $scope.drones.collection[droneIndex].id, icon:
					        { path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,scale: 6, fillColor: 'yellow', fillOpacity: 0.8, strokeColor: 'red', strokeWeight: 1, rotation:$scope.drones.collection[droneIndex].vehicle_status.heading}
				        })
			        $scope.markers[droneIndex].setMap(map);
		        }
		        $scope.markers[droneIndex].setPosition(new google.maps.LatLng($scope.drones.collection[droneIndex].vehicle_status.global_frame.lat, $scope.drones.collection[droneIndex].vehicle_status.global_frame.lon));

		        //draw authorized fly zones
				if ($scope.zones[droneIndex]) {
			        //console.log('Zone already exists');
		        } else
				{
					if (($scope.drones.collection[droneIndex].vehicle_status.zone) && ($scope.drones.collection[droneIndex].vehicle_status.armed_status=="ARMED")){
						if ($scope.drones.collection[droneIndex].vehicle_status.zone.shape) {
							var center={lat:$scope.drones.collection[droneIndex].vehicle_status.zone.shape.lat,lng:$scope.drones.collection[droneIndex].vehicle_status.zone.shape.lon};
							$scope.zones[droneIndex] = new google.maps.Circle({strokeColor:'#22FF22', strokeOpacity:0.8,fillColor:'#00FF00',fillOpacity:0.10,center:center ,radius: $scope.drones.collection[droneIndex].vehicle_status.zone.shape.radius,map:map});
						}
					}
				}

				//draw advisories

				var newAdvisoriesLength=Object.keys($scope.advisories.collection).length;
				if (newAdvisoriesLength>$scope.advisoriesCount){
					console.log('advisories changed');
					$scope.advisoriesCount=newAdvisoriesLength;

					//delete old advisories
					for (var mappedAdvisoryIndex in $scope.mappedAdvisories) {
						$scope.mappedAdvisories[mappedAdvisoryIndex].setMap(null);
					}
					$scope.mappedAdvisories.splice(0, $scope.mappedAdvisories.length);


					for (var advisoryKey in $scope.advisories.collection) {
						console.log('advisoryKey',advisoryKey);
						var center={lat:$scope.advisories.collection[advisoryKey].latitude,lng:$scope.advisories.collection[advisoryKey].longitude};
						$scope.mappedAdvisories.push(new google.maps.Circle({strokeColor:'#FF2222', strokeOpacity:0.8,fillColor:'#FF0000',fillOpacity:0.10,center:center ,radius: 2000,map:map}));
					}
				}

		    }
		});

	}



	function deleteAllMarkers() {
		for(var droneIndex in $scope.markers) {
		    $scope.markers[droneIndex].setMap(null);
		}
		$scope.markers.splice(0, $scope.markers.length);
	}

	function deleteAllZones() {
		for(var droneIndex in $scope.zones) {
		    $scope.zones[droneIndex].setMap(null);
		}
		$scope.zones.splice(0, $scope.zones.length);
	}

	function deleteAllAdvisories() {
		for(var advisoryIndex in $scope.mappedAdvisories) {
		    $scope.mappedAdvisories[advisoryIndex].setMap(null);
		}
		$scope.mappedAdvisories.splice(0, $scope.mappedAdvisories.length);
		$scope.advisoriesCount=0;
	}

	$scope.selectIndividual=function(inDrone) {
		console.log('Selected drone',inDrone);
		droneService.droneId=inDrone.id;
		$location.path('/individual')

	}


	$scope.$on('$destroy', function() {
	  // clean up stuff
	  	console.log('###################################################');
	  	console.log('Unloading Main Controller');
		droneService.apiURL=$scope.apiURL;
		$interval.cancel(mapIntervalTimer);
		$interval.cancel(deleteMarketsTimer);
		$interval.cancel(deleteZonesTimer);
		$interval.cancel(deleteAdvisoriesTimer);

		deleteAllMarkers();
		deleteAllZones();
		deleteAllAdvisories();

	})

	}]);

