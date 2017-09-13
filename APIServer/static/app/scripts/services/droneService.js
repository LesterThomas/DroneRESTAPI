angular.module('droneFrontendApp')
.service('droneService',['$http','$interval','$rootScope', function($http,$interval,$rootScope) {
	var self=this;
    this.droneId=-1;
    this.apiURL='HTTP://test.droneapi.net/'
    this.consoleRootURL='HTTP://test.droneapi.net:1237'
    this.droneName='';
    this.lat=0;
    this.lon=0;
    this.alt=0;
    this.dir=0;
    this.drones={"collection":[]};
	this.advisories={"collection":{},"max_safe_distance":0};


	var intervalTimer = $interval(updateDrones, 250);
	updateDrones();
	//this.queryAdvisories(51.3793,-1.1954);
	function updateDrones() {
        if ( $rootScope.loggedInUser) {
			$http.get(self.apiURL + 'vehicle?status=true',{headers: {'APIKEY': $rootScope.loggedInUser.api_key }}).
			    then(function(data, status, headers, config) {
						console.debug('API get success',data,status);
						self.drones.collection=data.data._embedded.vehicle;

						for ( var droneId in self.drones.collection){
								//manipulate the model
							var drone=self.drones.collection[droneId];
							console.debug('Drone:',drone);
							if (drone.vehicle_status){
								if (drone.vehicle_status.armed==true) {
									drone.vehicle_status.armed_status="ARMED";
									drone.vehicle_status.armed_colour={color:'red'};
								} else {
									drone.vehicle_status.armed_status="DISARMED";
									drone.vehicle_status.armed_colour={color:'green'};
								}
								if (drone.vehicle_status.last_heartbeat<1) {
									drone.vehicle_status.heartbeat_status="OK";
									drone.vehicle_status.heartbeat_colour={color:'green'};
								} else {
									drone.vehicle_status.heartbeat_status="Err- " + Math.round(drone.vehicle_status.last_heartbeat) + " s";
									drone.vehicle_status.heartbeat_colour={color:'red'};
								}
								if (drone.vehicle_status.ekf_ok==true) {
									drone.vehicle_status.ekf_status="OK";
									drone.vehicle_status.ekf_colour={color:'green'};
								} else {
									drone.vehicle_status.ekf_status="EFK ERROR";
									drone.vehicle_status.ekf_colour={color:'red'};
								}
								drone.vehicle_status.distance_home= Math.sqrt((drone.vehicle_status.local_frame.east)*(drone.vehicle_status.local_frame.east)+(drone.vehicle_status.local_frame.north)*(drone.vehicle_status.local_frame.north));
							}
						}



					},
					function(data, status, headers, config) {
					  // log error
						console.log('API get error',data, status, headers, config);
					});
            }
		}

	this.queryAdvisories=function(inLat,inLon){
			var airmapURL='https://api.airmap.com/status/v2/point?latitude='+inLat+'&longitude='+inLon+'&buffer=10000&weather=true';
			console.log('AIRMAP URL:',airmapURL);
			$http.get(airmapURL, {
				headers: {'X-API-Key': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVkZW50aWFsX2lkIjoiY3JlZGVudGlhbHxBendXTDJKaGF4MEVRWUNlQlJCR2VVb0dKV2VhIiwiYXBwbGljYXRpb25faWQiOiJhcHBsaWNhdGlvbnxrOVFBZEJ3aE93M0JQT2ZZRzZlZ0pVUXdFRVhMIiwib3JnYW5pemF0aW9uX2lkIjoiZGV2ZWxvcGVyfE43Z2Q2eURobkdubnFOc2Q5eEpiS2hiWm1vWCIsImlhdCI6MTUwMDIwMTczOH0.HX-RbNqEGq_ic1ys0U5dvZCtvCPCgz2_z8ggxv5SHdo'}
				}).
			    then(function(data, status, headers, config) {
					console.log('AIRMAP API get success',data, status, headers, config);
					var inAdvisories=data.data.data.advisories;
					var shortest_distance=3000;
					for (var advisoryIndex in inAdvisories){
						console.log('Advisory:',inAdvisories[advisoryIndex]);
						console.log('Advisory id:',inAdvisories[advisoryIndex].id);
                        if (inAdvisories[advisoryIndex].color!='green') {
    						if (inAdvisories[advisoryIndex].distance<shortest_distance){
    							shortest_distance=inAdvisories[advisoryIndex].distance;
    						}
                        }
						self.advisories.collection[inAdvisories[advisoryIndex].id]=inAdvisories[advisoryIndex];
					}
					//calculate max safe distance

					self.advisories.max_safe_distance=shortest_distance;
					console.log('Query Advisories',self.advisories);

				},
				function(data, status, headers, config) {
				  // log error
					console.log('AIRMAP API get error',data, status, headers, config);
				});

	}

}]);


