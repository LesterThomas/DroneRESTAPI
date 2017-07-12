'use strict';
/**
 * @ngdoc function
 * @name sbAdminApp.controller:MainCtrl
 * @description
 * # MainCtrls
 * Controller of the sbAdminApp
 */
angular.module('sbAdminApp')
  .controller('PerformanceCtrl', ['$scope', '$timeout','$interval','$http', 'logsService','containersService',  function ($scope, $timeout,$interval,$http,logsService,containersService) {

    
    $scope.logger = logsService.logger;
    $scope.console=containersService.console;
    
        

    containersService.console.queryDockerContainers($scope);


    //function called at intervals to update the Graph data by calling the Stats and Logs functions
    $scope.queryDockerLogsStats=function() {
      	$('#heartbeat').toggle();
        $scope.logger.getDockerStats($scope);
        $scope.logger.getDockerLogs($scope);
    }
  
    function getRunningContainers() {
        containersService.console.queryDockerContainers($scope)
    }
    
    //start periodic checking
    if ($scope.console.containersTimer) { }
        else {
        $scope.console.containersTimer=$interval(getRunningContainers, 2000);
        }


    //start periodic checking. Once the interval timer is created, it is never destroyed (so the graph continue even if you are on a different page).
    if (containersService.console.initiated) {
      	} else {
      	  $scope.logger.intervalTimer=$interval($scope.queryDockerLogsStats, 1000);
    	    containersService.console.initiated=true;
      	//alert('starting interval');     
      	}
    

}]);
