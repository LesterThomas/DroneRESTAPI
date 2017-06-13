angular.module('droneFrontendApp')
.service('individualDrone', function() {
    this.droneId=-1;
    this.apiURL='http://localhost:1235/';//'HTTP://droneapi.ddns.net:1235/'
    this.consoleRootURL='http://localhost:1235/static/app';//'HTTP://droneapi.ddns.net:1235/static/app'
    this.droneName='';
});