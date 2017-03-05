'use strict';

/**
 * @ngdoc function
 * @name droneFrontendApp.controller:IndividualCtrl
 * @description
 * # IndividualCtrl
 * Controller of the droneFrontendApp
 */
   
angular.module('droneFrontendApp')
  .controller('IndividualCtrl', ['$scope', '$http','NgMap','$interval','$location','individualDrone',function ($scope,$http,NgMap,$interval,$location,individualDrone) {
	  	  
  	console.log('Started controller'); 
  	$scope.apiURL='http://localhost:1235/'; //http://sail.vodafone.com/drone/';

	$scope.status='Loading';
	$scope.mission={};
	$scope.actions={availableActions:{}};
	$scope.actionLog={items:[]};

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
	var intervalTimer = $interval(updateDrone, 500);
	var intervalActionsTimer = $interval(updateActions, 2000);
	updateActions();
	function updateDrone() {
		$http.get($scope.apiURL + 'vehicle/'+individualDrone.droneId+'/').
		    then(function(data, status, headers, config) {
					//console.log('API get success',data,status);	
					$scope.vehicleStatus=data.data.vehicleStatus;
					//manipulate the model
					$scope.vehicleStatus.altitude=-$scope.vehicleStatus.local_frame.down;
					if ($scope.vehicleStatus.armed==true) {
						$scope.vehicleStatus.armed_status="ARMED";
						$scope.vehicleStatus.armed_colour={color:'red'};
					} else {
						$scope.vehicleStatus.armed_status="DISARMED";
						$scope.vehicleStatus.armed_colour={color:'green'};
					}
					if ($scope.vehicleStatus.last_heartbeat<1) {
						$scope.vehicleStatus.heartbeat_status="OK";
						$scope.vehicleStatus.heartbeat_colour={color:'green'};
					} else {
						$scope.vehicleStatus.heartbeat_status="Last Heartbeat " + Math.round($scope.vehicleStatus.last_heartbeat) + " s";
						$scope.vehicleStatus.heartbeat_colour={color:'red'};
					}
					if ($scope.vehicleStatus.ekf_ok==true) {
						$scope.vehicleStatus.ekf_status="OK";
						$scope.vehicleStatus.ekf_colour={color:'green'};
					} else {
						$scope.vehicleStatus.ekf_status="EFK ERROR";
						$scope.vehicleStatus.ekf_colour={color:'red'};
					}
					$scope.vehicleStatus.distance_home= Math.sqrt(($scope.vehicleStatus.local_frame.east)*($scope.vehicleStatus.local_frame.east)+($scope.vehicleStatus.local_frame.north)*($scope.vehicleStatus.local_frame.north));
					
					NgMap.getMap().then(function(map) {
					if ($scope.markers.length>0) {
						//console.log('Marker already exists');
					} else
					{
						$scope.markers[0] = new google.maps.Marker({ title: "Drone: " + individualDrone.droneId, icon: 
								{ path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,scale: 6, fillColor: 'yellow', fillOpacity: 0.8, strokeColor: 'red', strokeWeight: 1, rotation:$scope.vehicleStatus.heading} 
							});

						map.setCenter(new google.maps.LatLng( $scope.vehicleStatus.global_frame.lat, $scope.vehicleStatus.global_frame.lon ) );
						$scope.markers[0].setMap(map);

					}

					//if heading has changed, recreate icon
					if ($scope.markers[0].icon.rotation != $scope.vehicleStatus.heading) {
						$scope.markers[0].setMap(null);
						$scope.markers[0] = new google.maps.Marker({ title: "Drone: " + individualDrone.droneId, icon: 
								{ path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,scale: 6, fillColor: 'yellow', fillOpacity: 0.8, strokeColor: 'red', strokeWeight: 1, rotation:$scope.vehicleStatus.heading} 
							})
						$scope.markers[0].setMap(map);
					}
					$scope.markers[0].setPosition(new google.maps.LatLng($scope.vehicleStatus.global_frame.lat, $scope.vehicleStatus.global_frame.lon));
					



					//console.log('Marker:',$scope.markers[0]);
					//log data for graphs
					$scope.batteryCurrent.data[0].push($scope.vehicleStatus.battery.current);
					$scope.batteryCurrent.data[1].push($scope.vehicleStatus.battery.voltage);
					if ($scope.batteryCurrent.data[0].length>80) {
						$scope.batteryCurrent.data[0].shift();
					}
					if ($scope.batteryCurrent.data[1].length>80) {
						$scope.batteryCurrent.data[1].shift();
					}
					
					$scope.altVel.data[0].push(Math.round($scope.vehicleStatus.groundspeed*10)/10);
					$scope.altVel.data[1].push(-Math.round($scope.vehicleStatus.local_frame.down));
					if ($scope.altVel.data[0].length>80) {
						$scope.altVel.data[0].shift();
					}
					if ($scope.altVel.data[1].length>80) {
						$scope.altVel.data[1].shift();
					}
                              
				
					//console.log('Map center', map.getCenter());
				  });				
					
				},
				function(data, status, headers, config) {
				  // log error
					console.log('API get error',data, status, headers, config);
				});
			}

	function setActionText(inAction) {
		var latLonAltText='';
		if (inAction.coordinate){
			latLonAltText="lat '" + Math.round(inAction.coordinate[0]*10000)/10000 + "' lon '"+ Math.round(inAction.coordinate[1]*10000)/10000 + "' alt '"+ Math.round(inAction.coordinate[2]*100)/100; 
		} else {
			latLonAltText="No lat/lon/alt info";
		}
		var textDescription="Unknown command with id "+inAction.command+", " + latLonAltText + ", params " + inAction.param1 + ", "+inAction.param2+", "+inAction.param3;

		//Navigate to waypoint
		if (inAction.command==16){
			textDescription="Navigate to waypoint at "+ latLonAltText + "'.";
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
		if (inAction.command==21){
			textDescription="Land.";
		}
		//Takeoff
		if (inAction.command==22){
			textDescription="Takeoff to an altitude of " + Math.round(inAction.coordinate[2]*100)/100 + "m.";
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
		return textDescription
	}
			
	$scope.getMission = function() {
		$http.get($scope.apiURL + 'vehicle/'+individualDrone.droneId+'/missionActions').
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


	  
	$scope.actionButton = function(inAction) {
		console.log('Button Clicked',inAction);
		var payload={};
		for (var i=0;i<inAction.attributes.length;i++) {
			payload[inAction.attributes[i].name]=inAction.attributes[i].value;
		}
		payload['name']=inAction.name;
		console.log('Sending POST with payload ',payload);

		$http.post($scope.apiURL + 'vehicle/'+individualDrone.droneId+'/action',payload,{
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
		$http.get($scope.apiURL + 'vehicle/'+individualDrone.droneId+'/action').
		    then(function(data, status, headers, config) {
					console.log('API action get success',data,status);	
					//add or delete actions - if unchanged then leave model unchanged
					
					//$scope.actions.availableActions=data.data.availableActions;
					
					//manipulate the model
					for(var action in data.data.availableActions) {
						var actionName=data.data.availableActions[action].name;
						if ($scope.actions.availableActions[actionName]) {  //if action already exists, do nothing
						} else
						{
							$scope.actions.availableActions[actionName]=data.data.availableActions[action];
							
							
							$scope.actions.availableActions[actionName].attributes=[];
							for(var i in $scope.actions.availableActions[actionName].samplePayload) {
								if (i!='name'){//do not push the name attribute
									$scope.actions.availableActions[actionName].attributes.push({name:i,value:$scope.actions.availableActions[actionName].samplePayload[i]});
									console.log (i,$scope.actions.availableActions[actionName].samplePayload[i]);
								}
							}
						}
					}
					//check if actions are no longer present
					for(var action in $scope.actions.availableActions) {
						var actionName=$scope.actions.availableActions[action].name;
						var found=false;
						for (var index in data.data.availableActions) {
							if (data.data.availableActions[index].name==actionName) {
								found=true;
							}
						}
						if (found==false) { //remove action
							delete $scope.actions.availableActions[action];
						}

					}
					
					
						
				},
				function(data, status, headers, config) {
				  // log error
					console.log('API actions get error',data, status, headers, config);
				});
			}
	
	console.log('Finished calling APIs'); 
	


  

  }]);
