'use strict';

/**
 * @ngdoc function
 * @name droneFrontendApp.controller:StartMissionCtrl
 * @description
 * # StartMissionCtrl
 * Controller of the StartMission view that was created for the Softfire Hackathon. It selects the first drone from the inventory and
 * commands it to follow the mission. If there are no drones in the inventory, it shows an error message.
 */

angular.module('droneFrontendApp')
  .controller('StartMissionCtrl', ['$scope', '$http','NgMap','$interval','$location','droneService','$rootScope',function ($scope,$http,NgMap,$interval,$location,droneService,$rootScope) {

  console.log('Started startMission controller');
  $scope.apiURL=droneService.apiURL;
  $scope.consoleRootURL=droneService.consoleRootURL;
  $scope.drones=droneService.drones;
  droneService.droneId='';
	  
  var user_payload={name:"Lester Thomas",email:"lesterthomas@hotmail.com",id:"10211950448669833",id_provider:"Facebook"};
  console.log('Sending getting API Key - POST with payload ',user_payload);

  $http.post($scope.apiURL + 'user',user_payload,{
      headers : {
	'Content-Type' : 'application/json; charset=UTF-8'}
	}).then(function(data, status, headers, config) {
	  $rootScope.loggedInUser= data.data;
	  console.log('API user POST success',data,status);
	  $scope.checkDroneId = $interval(getDroneFromInventory, 250);
	},
	function(data, status, headers, config) {
	  // log error
	  console.log('API actions POST error',data, status, headers, config);
	});
	  	  

    
	

	function getDroneFromInventory() {
		console.log('Calling getDroneFromInventory to get id of first Drone' );
		if (droneService.droneId=='') 
		{
			if ($scope.drones.collection.length>0) {
				droneService.droneId=$scope.drones.collection[0].id;
				$interval.cancel($scope.checkDroneId);

			}
		}

	}
					
	var myVideo = document.getElementById("videoPlayer"); 
	myVideo.pause(); 


    $scope.executeCommandList=[
	    {assert:[{name:"is_armable",value:true,description:"Waiting for drone to be armable."}], name:"Check", attributes:[{name:"Drone Telemetry",value:"OK"}]},
	    {assert:[], name:"Check", attributes:[{name:"5G Connectivity",value:"Data Not-Available"}]},
	    {assert:[], name:"Check", attributes:[{name:"Weather",value:"OK"}]},
	    {assert:[], name:"Check", attributes:[{name:"No-Fly Zones",value:"OK"}]},
	    {assert:[], name:"Arm", attributes:[]},
	     {assert:[], name:"Takeoff", attributes:[{name:"height",value:"10"}]},
	     {assert:[], name:"Start-Mission", attributes:[]}
    ];
    $scope.executeCommandIndex=0;
	  
    $scope.status='Loading';
	$scope.mission={};
	$scope.commands={availableCommands:{}};
	$scope.commandLog={items:[]};
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
                                stepValue: 2,
                                max:40
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
                                max:25
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
                                max:12
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
                                steps: 8,
                                stepValue: 10,
                                max:70
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


	//if vehicle is disarmed then delete the authorized zone
	$scope.$watch("drones.collection[droneIndex].vehicle_status.armed_status", function (newValue) {
		console.log("Armed status",newValue);
		if (newValue=="DISARMED"){
			if ($scope.zones.length>0) {
				$scope.zones[0].setMap(null);
				$scope.zones.splice(0, 1);
			}
		}
	});



	function redrawAdvisories(){

		if (($scope.drones.collection[$scope.droneIndex].vehicle_status.armed_status=='DISARMED') && ($scope.safeToArm=='untested')){
			$scope.safeToArm='tested';
			droneService.queryAdvisories($scope.drones.collection[$scope.droneIndex].vehicle_status.global_frame.lat,$scope.drones.collection[$scope.droneIndex].vehicle_status.global_frame.lon);
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


	var intervalTimer = $interval(updateDrone, 250);
	var intervalActionsTimer = $interval(updateCommands, 3000);
	function updateDrone() {

        if(typeof $scope.drones.collection[$scope.droneIndex] === 'undefined') {
            // does not exist
		$scope.droneIndex=-1;
		for (var i in $scope.drones.collection){
			if ($scope.drones.collection[i].id==droneService.droneId){
				$scope.droneIndex=i;
			}
		}
			
		
        }
        else {
            // does exist



			NgMap.getMap().then(function(map) {
			if ($scope.markers.length>0) {
				//console.log('Marker already exists');
			} else
			{
				$scope.markers[0] = new google.maps.Marker({ title: "Drone: " + droneService.droneId, icon:
						{ path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,scale: 8, fillColor: 'yellow', fillOpacity: 0.8, strokeColor: 'red', strokeWeight: 1, rotation:$scope.drones.collection[$scope.droneIndex].vehicle_status.heading}
					});

				map.setCenter(new google.maps.LatLng( $scope.drones.collection[$scope.droneIndex].vehicle_status.global_frame.lat, $scope.drones.collection[$scope.droneIndex].vehicle_status.global_frame.lon ) );
				$scope.markers[0].setMap(map);

			}

			//if heading has changed, recreate icon
			if ($scope.markers[0].icon.rotation != $scope.drones.collection[$scope.droneIndex].vehicle_status.heading) {
				$scope.markers[0].setMap(null);
				$scope.markers[0] = new google.maps.Marker({ title: "Drone: " + droneService.droneId, icon:
						{ path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,scale: 6, fillColor: 'yellow', fillOpacity: 0.8, strokeColor: 'red', strokeWeight: 1, rotation:$scope.drones.collection[$scope.droneIndex].vehicle_status.heading}
					})
				$scope.markers[0].setMap(map);
			}
			$scope.markers[0].setPosition(new google.maps.LatLng($scope.drones.collection[$scope.droneIndex].vehicle_status.global_frame.lat, $scope.drones.collection[$scope.droneIndex].vehicle_status.global_frame.lon));
	        //draw authorized fly zones
			if ($scope.zones.length>0) {
		        //console.log('Zone already exists');
	        } else
			{
				if (($scope.drones.collection[$scope.droneIndex].vehicle_status.zone) && ($scope.drones.collection[$scope.droneIndex].vehicle_status.armed_status=="ARMED")){
					if ($scope.drones.collection[$scope.droneIndex].vehicle_status.zone.shape) {
						var center={lat:$scope.drones.collection[$scope.droneIndex].vehicle_status.zone.shape.lat,lng:$scope.drones.collection[$scope.droneIndex].vehicle_status.zone.shape.lon};
						$scope.zones[0] = new google.maps.Circle({strokeColor:'#22FF22', strokeOpacity:0.8,fillColor:'#00FF00',fillOpacity:0.10,center:center ,radius: $scope.drones.collection[$scope.droneIndex].vehicle_status.zone.shape.radius,map:map});
					}
				}
			}






			//console.log('Marker:',$scope.markers[0]);
			//log data for graphs
			$scope.batteryCurrent.data[0].push($scope.drones.collection[$scope.droneIndex].vehicle_status.battery.current);
			$scope.batteryCurrent.data[1].push($scope.drones.collection[$scope.droneIndex].vehicle_status.battery.voltage);
			if ($scope.batteryCurrent.data[0].length>80) {
				$scope.batteryCurrent.data[0].shift();
			}
			if ($scope.batteryCurrent.data[1].length>80) {
				$scope.batteryCurrent.data[1].shift();
			}

			$scope.altVel.data[0].push(Math.round($scope.drones.collection[$scope.droneIndex].vehicle_status.groundspeed*10)/10);
			$scope.altVel.data[1].push(Math.round($scope.drones.collection[$scope.droneIndex].vehicle_status.global_relative_frame.alt));
			if ($scope.altVel.data[0].length>80) {
				$scope.altVel.data[0].shift();
			}
			if ($scope.altVel.data[1].length>80) {
				$scope.altVel.data[1].shift();
			}


			//console.log('Map center', map.getCenter());
		  });

        }
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
        //Power on
        if (inAction.command==401){
            textDescription="Vehicle powered on.";
        }
        //Power off
        if (inAction.command==402){
            textDescription="Vehicle powered off.";
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
		$http.get($scope.apiURL + 'vehicle/'+droneService.droneId+'/mission',{headers: {'APIKEY': $rootScope.loggedInUser.api_key }}).
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
							for(var commandIndex in $scope.mission.items) {
								var missionAction=$scope.mission.items[commandIndex];
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
			        'Content-Type' : 'application/json; charset=UTF-8',
                    'APIKEY': $rootScope.loggedInUser.api_key
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

	$scope.commandButton = function(inAction) {
		console.log('Button Clicked',inAction);
		var payload={};
		for (var i=0;i<inAction.attributes.length;i++) {
			payload[inAction.attributes[i].name]=inAction.attributes[i].value;
		}
		payload['name']=inAction.name;

		if (inAction.name=="Check"){
			    var commandItem={"name":inAction.name,"textDescription":inAction.attributes[0].name + " " + inAction.attributes[0].value,"status":"success" }
			    $scope.commandLog.items.push(commandItem);

			
		}
		else {
			var myVideo = document.getElementById("videoPlayer"); 
			myVideo.play(); 
			  		
			console.log('Sending POST with payload ',payload);

			$http.post($scope.apiURL + 'vehicle/'+droneService.droneId+'/command',payload,{
				headers : {
					'Content-Type' : 'application/json; charset=UTF-8',
			'APIKEY': $rootScope.loggedInUser.api_key
				}
			}).then(function(data, status, headers, config) {

		    //test for error
		    if (typeof data.data.error  === 'undefined') {
					var commandItem=data.data.command;
					commandItem['textDescription']=setActionText(commandItem);

					$scope.commandLog.items.push(commandItem);
					console.log('API command POST success',data,status);
			}
			else {
			    var commandItem={"name":"Power-On","error":"Unknown error","status":"Error" }
			    commandItem['textDescription']=setActionText(commandItem);

			    $scope.commandLog.items.push(commandItem);
			    console.log('API command POST returned error',data,status);


			}

			},
			function(data, status, headers, config) {
			  // log error
				console.log('API commands POST error',data, status, headers, config);
			});
		}

	}

	function updateCommands() {

		
		//executeCommandList
		//executeCommandIndex
		if ($scope.executeCommandIndex==0) {
			

		    	$scope.getMission(); 
		}
		
		redrawAdvisories();
		
		if ($scope.executeCommandIndex<$scope.executeCommandList.length){
			console.log('Executing command ',$scope.executeCommandList[$scope.executeCommandIndex]);

			//test assertions
			var assertions_passed=true;
			var assertion_text="";
			for(var i=0;i<$scope.executeCommandList[$scope.executeCommandIndex].assert.length;i++){
				var assertion=$scope.executeCommandList[$scope.executeCommandIndex].assert[i];
				console.log('Checking assertion ',assertion);
				if ($scope.drones.collection[$scope.droneIndex].vehicle_status[assertion.name]!=assertion.value){
					assertions_passed=false;
					assertion_text=assertion.description;
				}
			}
			if (assertions_passed) {
				$scope.commandButton($scope.executeCommandList[$scope.executeCommandIndex]);
				$scope.executeCommandIndex++;	
			} else {
			    var commandItem={"name":$scope.executeCommandList[$scope.executeCommandIndex].name,"textDescription":assertion_text ,"status":"success" }
			    $scope.commandLog.items.push(commandItem);				
			}
		}
		
		
		
		/*
		$http.get($scope.apiURL + 'vehicle/'+droneService.droneId+'/command',{
            headers : {
                'APIKEY': $rootScope.loggedInUser.api_key
            }
        }).
		    then(function(data, status, headers, config) {
					console.log('API command get success',data,status);
					//add or delete commands - if unchanged then leave model unchanged

					//$scope.commands.availableCommands=data.data._actions;

					//manipulate the model
					for(var command in data.data._actions) {
						var commandName=data.data._actions[command].name;
						if ($scope.commands.availableCommands[commandName]) {  //if command already exists, do nothing
						} else
						{
							$scope.commands.availableCommands[commandName]=data.data._actions[command];


							$scope.commands.availableCommands[commandName].attributes=[];
							for(var i in $scope.commands.availableCommands[commandName].fields) {
								if ($scope.commands.availableCommands[commandName].fields[i]['name']!='name') {//do not push the name attribute
									console.log ($scope.commands.availableCommands[commandName].fields[i]['name'],$scope.commands.availableCommands[commandName].fields[i]['value']);
									$scope.commands.availableCommands[commandName].attributes.push({name:$scope.commands.availableCommands[commandName].fields[i]['name'],value:$scope.commands.availableCommands[commandName].fields[i]['value'] })
								}
								//if (i!='name'){//do not push the name attribute
								//	$scope.commands.availableCommands[commandName].attributes.push({name:i,value:$scope.commands.availableCommands[commandName].samplePayload[i]});
								//	console.log (i,$scope.commands.availableCommands[commandName].samplePayload[i]);
								//}
							}
						}
					}
					//check if commands are no longer present
					for(var command in $scope.commands.availableCommands) {
						var commandName=$scope.commands.availableCommands[command].name;
						var found=false;
						for (var index in data.data._actions) {
							if (data.data._actions[index].name==commandName) {
								found=true;
							}
						}
						if (found==false) { //remove command
							delete $scope.commands.availableCommands[command];
						}

					}

					//if command is Arm then additional checks necessary
					for(var command in $scope.commands.availableCommands) {
						var commandName=$scope.commands.availableCommands[command].name;
						if (commandName=='Arm'){
							console.log("Additional checks for Arm command");
							if ($scope.advisories.max_safe_distance<2500) { //if max safe distance is lass than 2500m then remove command (500m for drone line-of-sight and 2000m for advisory
								delete $scope.commands.availableCommands[command];
								//replace with warning
								$scope.commands.availableCommands['Cannot-Arm']={"name":"Cannot-Arm","title":"Cannot Arm: Check advisories (advisory distance is "+$scope.advisories.max_safe_distance+"m)","fields":[]};
							}
						}
					}




				},
				function(data, status, headers, config) {
				  // log error
					console.log('API commands get error',data, status, headers, config);
				});
*/
		
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
