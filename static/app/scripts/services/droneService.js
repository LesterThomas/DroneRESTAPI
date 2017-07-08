angular.module('droneFrontendApp')
.service('droneService',['$http','$interval', function($http,$interval) {
	var self=this;
    this.droneId=-1;
    this.apiURL='HTTP://192.168.1.67:1235/'
    this.consoleRootURL='HTTP://192.168.1.67:1235/static/app'
    this.droneName='';
    this.lat=0;
    this.lon=0;
    this.alt=0;
    this.dir=0;
    this.drones={"collection":[]};


	var intervalTimer = $interval(updateDrones, 250);
	updateDrones();
	function updateDrones() {
			$http.get(self.apiURL + 'vehicle?details=true').
			    then(function(data, status, headers, config) {
						console.debug('API get success',data,status);	
						self.drones.collection=data.data._embedded.vehicle;

						for ( var droneId in self.drones.collection){
								//manipulate the model
							var drone=self.drones.collection[droneId];
							console.debug('Drone:',drone);	
							if (drone.vehicleStatus){
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
									drone.vehicleStatus.heartbeat_status="Err- " + Math.round(drone.vehicleStatus.last_heartbeat) + " s";
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
						}
					

	                          
					},
					function(data, status, headers, config) {
					  // log error
						console.log('API get error',data, status, headers, config);
					});

		}


}]);