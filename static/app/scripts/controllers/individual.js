'use strict';

/**
 * @ngdoc function
 * @name droneFrontendApp.controller:IndividualCtrl
 * @description
 * # IndividualCtrl
 * Controller of the droneFrontendApp
 */
   
angular.module('droneFrontendApp')
  .controller('IndividualCtrl', ['$scope', '$http','NgMap','$interval','$location','droneService',function ($scope,$http,NgMap,$interval,$location,droneService) {
	  	  
  	console.log('Started individual controller'); 
    $scope.apiURL=droneService.apiURL;
    $scope.consoleRootURL=droneService.consoleRootURL;
	$scope.drones=droneService.drones;
	$scope.droneIndex=-1;
	for (var i in $scope.drones.collection){
		if ($scope.drones.collection[i].id==droneService.droneId){
			$scope.droneIndex=i;
		}
	}

    $scope.status='Loading';
	$scope.mission={};
	$scope.actions={availableActions:{}};
	$scope.actionLog={items:[]};
	$scope.simEnvironment=[];
	$scope.simParamSelected='';
	$scope.simParamValue='';
	$scope.zones=[];
	$scope.mappedAdvisories=[];
	$scope.advisories=droneService.advisories;
	$scope.advisoriesCount=0;
	$scope.safeToArm='untested';
	
    $scope.droneIcon = {
      path: 'M 0 0 L -35 -100 L 35 -100 z',
      fillColor: '#3884ff',
      fillOpacity: 0.7,
      scale: 1,
      strokeColor: '#356cde',
      rotation: 90,
      strokeWeight: 1
    };
    
	//graph data for Battery
	$scope.batteryCurrent = {};
	
    $scope.batteryCurrent.labels= ['','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','',''];
    $scope.batteryCurrent.series= ['Current','Voltage'];
    $scope.batteryCurrent.data=  [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]];
    $scope.batteryCurrent.options= { animation:false, scaleOverride:true, scaleStepWidth: 50, scaleStartValue: 0, scaleSteps:10,   scaleBeginAtZero: true, 
		scales: {
                    xAxes: [{
                            display: false,

                        }],
                    yAxes: [{
							position: 'left',
							id: 'y-axis-1',
                            display: true,
							scaleLabel: {
									display: true,
									labelString: 'Current (A)'
								},
                            ticks: {
								beginAtZero: true,
                                steps: 10,
                                stepValue: 5,
                                max: 50
                            }
                        },{
							position: 'right',
							id: 'y-axis-2',
                            display: true,
							scaleLabel: {
									display: true,
									labelString: 'Voltage (V)'
								},
                            ticks: {
								beginAtZero: true,
                                steps: 10,
                                stepValue: 2,
                                max: 16
                            }
                        }]
		}
	};
	
	$scope.batteryCurrent.datasetOverride = [{ yAxisID: 'y-axis-1' }, { yAxisID: 'y-axis-2' }];
	
	
    $scope.batteryCurrent.onClick= function (points, evt) {
				console.log(points, evt);
			};

	
	//graph data for Battery
	$scope.altVel = {};
	
    $scope.altVel.labels= ['','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','',''];
    $scope.altVel.series= ['Velocity','Altitude'];
    $scope.altVel.data=  [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]];
    $scope.altVel.options= { animation:false, scaleOverride:true, scaleStepWidth: 50, scaleStartValue: 0, scaleSteps:10,   scaleBeginAtZero: true, 
		scales: {
                    xAxes: [{
                            display: false,

                        }],
                    yAxes: [{
							position: 'left',
							id: 'y-axis-1',
                            display: true,
							scaleLabel: {
									display: true,
									labelString: 'Velocity (Km/h)'
								},
                            ticks: {
								beginAtZero: true,
                                steps: 10,
                                stepValue: 5,
                                max: 10
                            }
                        },{
							position: 'right',
							id: 'y-axis-2',
                            display: true,
							scaleLabel: {
									display: true,
									labelString: 'Altitude (M)'
								},
                            ticks: {
								beginAtZero: true,
                                steps: 6,
                                stepValue: 10,
                                max: 50
                            }
                        }]
		}
	};
	
	$scope.altVel.datasetOverride = [{ yAxisID: 'y-axis-1' }, { yAxisID: 'y-axis-2' }];
	
	
    $scope.altVel.onClick= function (points, evt) {
				console.log(points, evt);
			};

			
	$scope.markers=[];
	$scope.flightPath=null;
	//console.log('Calling API'); 
	getSimEnvironment();
	function getSimEnvironment() {
	$http.get($scope.apiURL + 'vehicle/'+droneService.droneId+'/simulator').
	    then(function(data, status, headers, config) {
				console.log('getSimEnvironment API get success',data,status);	
				$scope.simEnvironment=data.data.simulatorParams;
			},
				function(data, status, headers, config) {
				  // log error
					console.log('getSimEnvironment API get error',data, status, headers, config);
				});
			}

	function updateSimEnvironment(key, value){
		console.log('simEnvironment.' + key + ' value changed to ',value);	
		var payload={"parameter":key,"value":parseFloat(value)};
		console.log('Sending POST with payload ',payload);

		$http.post($scope.apiURL + 'vehicle/'+droneService.droneId+'/simulator',payload,{
		    headers : {
		        'Content-Type' : 'application/json; charset=UTF-8'
		    }
			}).then(function(data, status, headers, config) {
					var actionItem=data.data.action;
					console.log('API  action POST success',data,status);
				},
				function(data, status, headers, config) {
				  	// log error
					console.log('API actions POST error',data, status, headers, config);
				});


	}

	$scope.simParamUpdateButton = function(){
		console.log("Setting simulator parameter '"+$scope.simParamSelected+"' to '" + $scope.simParamValue + "'.");

		updateSimEnvironment($scope.simParamSelected,$scope.simParamValue);

	}

	//if vehicle is disarmed then delete the authorized zone
	$scope.$watch("drones.collection[droneIndex].vehicleStatus.armed_status", function (newValue) {		
		console.log("Armed status",newValue);	
		if (newValue=="DISARMED"){
			if ($scope.zones.length>0) {
				$scope.zones[0].setMap(null);
				$scope.zones.splice(0, 1);
			}
		}
	});
	


	function redrawAdvisories(){
	
		if (($scope.drones.collection[$scope.droneIndex].vehicleStatus.armed_status=='DISARMED') && ($scope.safeToArm=='untested')){
			$scope.safeToArm='tested';
			droneService.queryAdvisories($scope.drones.collection[$scope.droneIndex].vehicleStatus.global_frame.lat,$scope.drones.collection[$scope.droneIndex].vehicleStatus.global_frame.lon);
		}

	
		NgMap.getMap().then(function(map) {
			//console.log('Individual Map',map);
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
		});
	}
	
	
	$scope.$watch("simParamSelected", function (newValue) {			
		$scope.simParamValue=$scope.simEnvironment[newValue];
	});

	var intervalTimer = $interval(updateDrone, 250);
	var intervalActionsTimer = $interval(updateActions, 2000);
	function updateDrone() {
						
			NgMap.getMap().then(function(map) {
			if ($scope.markers.length>0) {
				//console.log('Marker already exists');
			} else
			{
				$scope.markers[0] = new google.maps.Marker({ title: "Drone: " + droneService.droneId, icon: 
						{ path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,scale: 8, fillColor: 'yellow', fillOpacity: 0.8, strokeColor: 'red', strokeWeight: 1, rotation:$scope.drones.collection[$scope.droneIndex].vehicleStatus.heading} 
					});

				map.setCenter(new google.maps.LatLng( $scope.drones.collection[$scope.droneIndex].vehicleStatus.global_frame.lat, $scope.drones.collection[$scope.droneIndex].vehicleStatus.global_frame.lon ) );
				$scope.markers[0].setMap(map);

			}

			//if heading has changed, recreate icon
			if ($scope.markers[0].icon.rotation != $scope.drones.collection[$scope.droneIndex].vehicleStatus.heading) {
				$scope.markers[0].setMap(null);
				$scope.markers[0] = new google.maps.Marker({ title: "Drone: " + droneService.droneId, icon: 
						{ path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,scale: 6, fillColor: 'yellow', fillOpacity: 0.8, strokeColor: 'red', strokeWeight: 1, rotation:$scope.drones.collection[$scope.droneIndex].vehicleStatus.heading} 
					})
				$scope.markers[0].setMap(map);
			}
			$scope.markers[0].setPosition(new google.maps.LatLng($scope.drones.collection[$scope.droneIndex].vehicleStatus.global_frame.lat, $scope.drones.collection[$scope.droneIndex].vehicleStatus.global_frame.lon));
	        //draw authorized fly zones
			if ($scope.zones.length>0) {
		        //console.log('Zone already exists');
	        } else
			{
				if (($scope.drones.collection[$scope.droneIndex].vehicleStatus.zone) && ($scope.drones.collection[$scope.droneIndex].vehicleStatus.armed_status=="ARMED")){
					if ($scope.drones.collection[$scope.droneIndex].vehicleStatus.zone.shape) {
						var center={lat:$scope.drones.collection[$scope.droneIndex].vehicleStatus.zone.shape.lat,lng:$scope.drones.collection[$scope.droneIndex].vehicleStatus.zone.shape.lon};
						$scope.zones[0] = new google.maps.Circle({strokeColor:'#22FF22', strokeOpacity:0.8,fillColor:'#00FF00',fillOpacity:0.10,center:center ,radius: $scope.drones.collection[$scope.droneIndex].vehicleStatus.zone.shape.radius,map:map}); 
					}
				}
			}

			
	



			//console.log('Marker:',$scope.markers[0]);
			//log data for graphs
			$scope.batteryCurrent.data[0].push($scope.drones.collection[$scope.droneIndex].vehicleStatus.battery.current);
			$scope.batteryCurrent.data[1].push($scope.drones.collection[$scope.droneIndex].vehicleStatus.battery.voltage);
			if ($scope.batteryCurrent.data[0].length>80) {
				$scope.batteryCurrent.data[0].shift();
			}
			if ($scope.batteryCurrent.data[1].length>80) {
				$scope.batteryCurrent.data[1].shift();
			}
			
			$scope.altVel.data[0].push(Math.round($scope.drones.collection[$scope.droneIndex].vehicleStatus.groundspeed*10)/10);
			$scope.altVel.data[1].push(Math.round($scope.drones.collection[$scope.droneIndex].vehicleStatus.global_relative_frame.alt));
			if ($scope.altVel.data[0].length>80) {
				$scope.altVel.data[0].shift();
			}
			if ($scope.altVel.data[1].length>80) {
				$scope.altVel.data[1].shift();
			}
                      
		
			//console.log('Map center', map.getCenter());
		  });	


			}

	function setActionText(inAction) {
		var latLonAltText='';
		if (inAction.coordinate){
			latLonAltText="lat '" + Math.round(inAction.coordinate[0]*10000)/10000 + "' lon '"+ Math.round(inAction.coordinate[1]*10000)/10000 + "' alt '"+ Math.round(inAction.coordinate[2]*100)/100 + "'"; 
		} else {
			latLonAltText="No lat/lon/alt info";
		}
		var textDescription="Unknown command with id "+inAction.command+", " + latLonAltText + ", params " + inAction.param1 + ", "+inAction.param2+", "+inAction.param3;

		//Navigate to waypoint
		if (inAction.command==16){
			textDescription="Navigate to waypoint at "+ latLonAltText + ".";
			if (inAction.param1>0){
				textDescription+=" Loiter for " + inAction.param1 + " seconds.";
			}
		}
		//Loiter
		if (inAction.command==17){
			textDescription="Loiter at " + latLonAltText + " for an unlimited time.";
		}
		//RTL
		if (inAction.command==20){
			textDescription="Return to Launch.";
		}
		//Land
		if (inAction.command==23){
			textDescription="Land at " + latLonAltText + ".";
		}
		//Takeoff
		if (inAction.command==22){
			textDescription="Takeoff to an altitude of " + Math.round(inAction.coordinate[2]*100)/100 + "m.";
		}
		//Arm
		if (inAction.command==400){
			textDescription="Vehicle armed.";
		}
		//Region of Interest
		if (inAction.command==80){
			textDescription="Set the Region of Interest to " + latLonAltText + ".";
		}
		//Navigate to spline waypoint
		if (inAction.command==82){
			textDescription="Navigate to waypoint at "+ latLonAltText + "' using a spline path.";
			if (inAction.param1>0){
				textDescription+=" Loiter for " + inAction.param1 + " seconds.";
			}
		}
		//start mission
		if (inAction.name=='Start-Mission'){
			textDescription="Start the pre-defined mission.";
			if (inAction.param1>0){
				textDescription+=" Loiter for " + inAction.param1 + " seconds.";
			}
		}
		//error
		if (inAction.status=='Error'){
			textDescription=inAction.error;
		}

		return textDescription
	}
			
	$scope.getMission = function() {
		$http.get($scope.apiURL + 'vehicle/'+droneService.droneId+'/mission').
		    then(function(data, status, headers, config) {
					console.log('API mission get success',data,status);	
					$scope.mission=data.data;
					console.log($scope.mission);
					//manipulate the model
					for(var missionActions in $scope.mission.items) {
						$scope.mission.items[missionActions].textDescription=setActionText($scope.mission.items[missionActions]);
					}



					NgMap.getMap().then(function(map) {
						
						if ($scope.mission.items.length>0) {
							//Mission polyline
							var flightPlanCoordinates = [];
							for(var actionIndex in $scope.mission.items) {
								var missionAction=$scope.mission.items[actionIndex];
								if (missionAction.command==20) {  
									//return-to-home so draw to planned home
									missionAction.coordinate=$scope.mission.plannedHomePosition.coordinate;
								}
								flightPlanCoordinates.push({lat:missionAction.coordinate[0],lng:missionAction.coordinate[1]});
							}
							if ($scope.flightPath) {
								//polyline already exists so remove from map and delete
								$scope.flightPath.setMap(null);
								$scope.flightPath=null;
							} 
							$scope.flightPath = new google.maps.Polyline({
							    path: flightPlanCoordinates,
							    geodesic: true,
							    strokeColor: '#FFFFFF',
							    strokeOpacity: 0.5,
							    strokeWeight: 2
							});
							$scope.flightPath.setMap(map);	
						}
					});




				},
				function(data, status, headers, config) {
				  // log error
					console.log('API mission get error',data, status, headers, config);
				});


	}

	$scope.disconnectDelete = function() {
		console.log('disconnectDelete Button Clicked');

		if (confirm('Confirm disconnect?')){
			//delete
			console.log('disconnectDelete confirmed');

			$http.delete($scope.apiURL + 'vehicle/'+droneService.droneId,{
			    headers : {
			        'Content-Type' : 'application/json; charset=UTF-8'
			    }}).then(function(data, status, headers, config) {
				console.log('API  action DELETE success',data,status);
				
			},
			function(data, status, headers, config) {
			  // log error
				console.log('API actions DELETE error',data, status, headers, config);
			});
			window.location=$scope.consoleRootURL;
		} 
	}
	  
	$scope.actionButton = function(inAction) {
		console.log('Button Clicked',inAction);
		var payload={};
		for (var i=0;i<inAction.attributes.length;i++) {
			payload[inAction.attributes[i].name]=inAction.attributes[i].value;
		}

		
		payload['name']=inAction.name;
		
		console.log('Sending POST with payload ',payload);

		$http.post($scope.apiURL + 'vehicle/'+droneService.droneId+'/action',payload,{
			headers : {
				'Content-Type' : 'application/json; charset=UTF-8'
			}
		}).then(function(data, status, headers, config) {
			var actionItem=data.data.action;
			actionItem['textDescription']=setActionText(actionItem);
	
			$scope.actionLog.items.push(actionItem);
			console.log('API  action POST success',data,status);
			
		},
		function(data, status, headers, config) {
		  // log error
			console.log('API actions POST error',data, status, headers, config);
		});
		

	}

	function updateActions() {
		
		redrawAdvisories();
		$http.get($scope.apiURL + 'vehicle/'+droneService.droneId+'/action').
		    then(function(data, status, headers, config) {
					console.log('API action get success',data,status);	
					//add or delete actions - if unchanged then leave model unchanged
					
					//$scope.actions.availableActions=data.data._actions;
					
					//manipulate the model
					for(var action in data.data._actions) {
						var actionName=data.data._actions[action].name;
						if ($scope.actions.availableActions[actionName]) {  //if action already exists, do nothing
						} else
						{
							$scope.actions.availableActions[actionName]=data.data._actions[action];
							
							
							$scope.actions.availableActions[actionName].attributes=[];
							for(var i in $scope.actions.availableActions[actionName].fields) {
								if ($scope.actions.availableActions[actionName].fields[i]['name']!='name') {//do not push the name attribute
									console.log ($scope.actions.availableActions[actionName].fields[i]['name'],$scope.actions.availableActions[actionName].fields[i]['value']);
									$scope.actions.availableActions[actionName].attributes.push({name:$scope.actions.availableActions[actionName].fields[i]['name'],value:$scope.actions.availableActions[actionName].fields[i]['value'] })
								}
								//if (i!='name'){//do not push the name attribute
								//	$scope.actions.availableActions[actionName].attributes.push({name:i,value:$scope.actions.availableActions[actionName].samplePayload[i]});
								//	console.log (i,$scope.actions.availableActions[actionName].samplePayload[i]);
								//}
							}
						}
					}
					//check if actions are no longer present
					for(var action in $scope.actions.availableActions) {
						var actionName=$scope.actions.availableActions[action].name;
						var found=false;
						for (var index in data.data._actions) {
							if (data.data._actions[index].name==actionName) {
								found=true;
							}
						}
						if (found==false) { //remove action
							delete $scope.actions.availableActions[action];
						}

					}
					
					//if action is Arm then additional checks necessary
					for(var action in $scope.actions.availableActions) {
						var actionName=$scope.actions.availableActions[action].name;
						if (actionName=='Arm'){
							console.log("Additional checks for Arm action");
							if ($scope.advisories.max_safe_distance<2500) { //if max safe distance is lass than 2500m then remove action (500m for drone line-of-sight and 2000m for advisory
								delete $scope.actions.availableActions[action];	
								//replace with warning
								$scope.actions.availableActions['Cannot-Arm']={"name":"Cannot-Arm","title":"Cannot Arm: Check advisories (advisory distance is "+$scope.advisories.max_safe_distance+"m)","fields":[]};
							}
						}
					}

					
					
						
				},
				function(data, status, headers, config) {
				  // log error
					console.log('API actions get error',data, status, headers, config);
				});
			}
			
	$scope.deleteAllAdvisories=function() {
		for(var advisoryIndex in $scope.mappedAdvisories) {
		    $scope.mappedAdvisories[advisoryIndex].setMap(null);
		}
		$scope.mappedAdvisories.splice(0, $scope.mappedAdvisories.length);
	}

			
	$scope.$on('$destroy', function() {
	  // clean up stuff
	  	console.log('###################################################'); 
	  	console.log('Unloading Individual Controller'); 
		$interval.cancel(intervalTimer);
		$interval.cancel(intervalActionsTimer);
		if ($scope.markers.length>0) {
			$scope.markers[0].setMap(null);
			$scope.markers.splice(0, 1);
		}
		if ($scope.zones.length>0) {
			$scope.zones[0].setMap(null);
			$scope.zones.splice(0, 1);
		}
		$scope.deleteAllAdvisories();
		droneService.apiURL=$scope.apiURL;
	})		
	
	console.log('Finished calling APIs'); 
  

  }]);
