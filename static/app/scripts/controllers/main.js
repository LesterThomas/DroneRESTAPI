'use strict';

/**
 * @ngdoc function
 * @name droneFrontendApp.controller:MainCtrl
 * @description
 * # MainCtrl
 * Controller of the droneFrontendApp
 */
   
angular.module('droneFrontendApp')
  .controller('MainCtrl', ['$scope', '$http','NgMap','$interval','$location',function ($scope,$http,NgMap,$interval,$location) {
	  

	  
	  
	  
	  
  	console.log('Started controller'); 
  	$scope.apiURL='http://sail.vodafone.com/drone/';

	$scope.status='Loading';
	$scope.vehicleStatus={};
	$scope.actions={availableActions:{}};
	//graph data for Battery
	$scope.batteryCurrent = {};
	
    $scope.batteryCurrent.labels= ['','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','',''];
    $scope.batteryCurrent.series= ['Current','Voltage'];
    $scope.batteryCurrent.data=  [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]];
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
	
    $scope.altVel.labels= ['','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','',''];
    $scope.altVel.series= ['Velocity','Altitude'];
    $scope.altVel.data=  [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]];
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
	//console.log('Calling API'); 
	var intervalTimer = $interval(updateDrone, 1000);
	var intervalActionsTimer = $interval(updateActions, 2000);
	updateActions();
	function updateDrone() {
		$http.get($scope.apiURL + 'vehicle/1/').
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
						$scope.vehicleStatus.heartbeat_status="No Heartbeat Received";
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
						$scope.markers[0] = new google.maps.Marker({ title: "Drone: " + 1 });
						map.setCenter(new google.maps.LatLng( $scope.vehicleStatus.global_frame.lat, $scope.vehicleStatus.global_frame.lon ) );
						$scope.markers[0].setMap(map);

					}
					$scope.markers[0].setPosition(new google.maps.LatLng($scope.vehicleStatus.global_frame.lat, $scope.vehicleStatus.global_frame.lon));
					
					//log data for graphs
					$scope.batteryCurrent.data[0].push($scope.vehicleStatus.battery.current);
					$scope.batteryCurrent.data[1].push($scope.vehicleStatus.battery.voltage);
					if ($scope.batteryCurrent.data[0].length>40) {
						$scope.batteryCurrent.data[0].shift();
					}
					if ($scope.batteryCurrent.data[1].length>40) {
						$scope.batteryCurrent.data[1].shift();
					}
					
					$scope.altVel.data[0].push(Math.round($scope.vehicleStatus.groundspeed));
					$scope.altVel.data[1].push(-Math.round($scope.vehicleStatus.local_frame.down));
					if ($scope.altVel.data[0].length>40) {
						$scope.altVel.data[0].shift();
					}
					if ($scope.altVel.data[1].length>40) {
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
			
	  
	$scope.actionButton = function(inAction) {
		console.log('Button Clicked',inAction);
		var payload={};
		for (var i=0;i<inAction.attributes.length;i++) {
			payload[inAction.attributes[i].name]=inAction.attributes[i].value;
		}
		payload['name']=inAction.name;
		console.log('Sending POST with payload ',payload);

		$http.post($scope.apiURL + 'vehicle/1/action',payload,{
    headers : {
        'Content-Type' : 'application/json; charset=UTF-8'
    }
}).then(function(data, status, headers, config) {
			console.log('API  action POST success',data,status);
			
		},
		function(data, status, headers, config) {
		  // log error
			console.log('API actions POST error',data, status, headers, config);
		});

	}

	function updateActions() {
		$http.get($scope.apiURL + 'vehicle/1/action').
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
