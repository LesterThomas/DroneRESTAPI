angular.module('droneFrontendApp')
.service('individualDrone', function() {
    this.droneId=-1;
    this.apiURL='http://droneapi.ddns.net:1235/';//'HTTP://192.168.1.67:1235/'; //http://sail.vodafone.com/drone/';
});