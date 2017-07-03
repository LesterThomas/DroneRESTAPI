'use strict';

/**
 * @ngdoc function
 * @name droneFrontendApp.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the droneFrontendApp
 */
   
angular.module('droneFrontendApp')
  .controller('MainCtrl', ['$scope', 'NgMap','$location','$interval','droneService',function ($scope,NgMap,$location,$interval,droneService) {
	  
  	console.log('Started Main controller'); 
  	$scope.apiURL=droneService.apiURL;
	$scope.drones=droneService.drones;
	$scope.markers=[];
	$scope.zones=[];


	var mapIntervalTimer = $interval(updateMap, 250);
	var deleteMarketsTimer = $interval(deleteAllMarkers, 5000);
	var deleteZonesTimer = $interval(deleteAllZones, 7000);
	updateMap();
	function updateMap() {

        NgMap.getMap().then(function(map) {
				
            var bounds=new google.maps.LatLngBounds();

            for(var droneIndex in $scope.drones.collection) {
            	bounds=bounds.extend({lat:$scope.drones.collection[droneIndex].vehicleStatus.global_frame.lat+0.003,lng:$scope.drones.collection[droneIndex].vehicleStatus.global_frame.lon+0.003});
            	bounds=bounds.extend({lat:$scope.drones.collection[droneIndex].vehicleStatus.global_frame.lat-0.003,lng:$scope.drones.collection[droneIndex].vehicleStatus.global_frame.lon-0.003});
            }


			for(var droneIndex in $scope.drones.collection) {

				//draw drones (markers)
				if ($scope.markers[droneIndex]) {
			        //console.log('Marker already exists');
		        } else
				{
			        $scope.markers[droneIndex] = new google.maps.Marker({ title: "Drone: " + $scope.drones.collection[droneIndex].vehicleStatus.id, icon: 
					{ path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,scale: 6, fillColor: 'yellow', fillOpacity: 0.8, strokeColor: 'red', strokeWeight: 1, rotation:$scope.drones.collection[droneIndex].vehicleStatus.heading} 
				    });
			        //map.setCenter(new google.maps.LatLng(avgLat, avgLon ) ); //Set map based on avg  Drone location
			        map.fitBounds(bounds);
			        $scope.markers[droneIndex].setMap(map);
		        }

		        //if heading has changed, recreate icon
		        if ($scope.markers[droneIndex].icon.rotation != $scope.drones.collection[droneIndex].vehicleStatus.heading) {
			        $scope.markers[droneIndex].setMap(null);
			        $scope.markers[droneIndex] = new google.maps.Marker({ title: "Drone: " + $scope.drones.collection[droneIndex].vehicleStatus.id, icon: 
					        { path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,scale: 6, fillColor: 'yellow', fillOpacity: 0.8, strokeColor: 'red', strokeWeight: 1, rotation:$scope.drones.collection[droneIndex].vehicleStatus.heading} 
				        })
			        $scope.markers[droneIndex].setMap(map);
		        }
		        $scope.markers[droneIndex].setPosition(new google.maps.LatLng($scope.drones.collection[droneIndex].vehicleStatus.global_frame.lat, $scope.drones.collection[droneIndex].vehicleStatus.global_frame.lon));

		        //draw authorized fly zones
				if ($scope.zones[droneIndex]) {
			        //console.log('Zone already exists');
		        } else
				{
					if ($scope.drones.collection[droneIndex].vehicleStatus.zone.shape) {
    					var center={lat:$scope.drones.collection[droneIndex].vehicleStatus.zone.shape.lat,lng:$scope.drones.collection[droneIndex].vehicleStatus.zone.shape.lon};
				        $scope.zones[droneIndex] = new google.maps.Circle({strokeColor:'#22FF22', strokeOpacity:0.8,fillColor:'#00FF00',fillOpacity:0.10,center:center ,radius: $scope.drones.collection[droneIndex].vehicleStatus.zone.shape.radius,map:map}); 
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

		deleteAllMarkers();	
		deleteAllZones();	

	})			

	}]);

