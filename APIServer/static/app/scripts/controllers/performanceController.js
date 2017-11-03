'use strict';
/**
 * @ngdoc function
 * @name sbAdminApp.controller:MainCtrl
 * @description
 * # MainCtrls
 * Controller of the sbAdminApp
 */
angular.module('droneFrontendApp')
  .controller('PerformanceCtrl', ['$scope', '$timeout','$interval','$http',   function ($scope, $timeout,$interval,$http) {
  $scope.stats=[];

  //graph data for Battery
  $scope.containers=[];
  $scope.containerIndex=[];
  $scope.proxyIndex=[];
  $scope.utilityContainerIndex=[];
  $scope.serverAPIIndex=[];
  $scope.workerAPIIndex=[];

  function addGraphBaseline(containerId){

    if ($scope.stats[containerId].image.includes('dronesim')){
      $scope.containerIndex.push(containerId);
    }
    else if ($scope.stats[containerId].image.includes('droneproxy')){
      $scope.containerIndex.push(containerId);
    } else if  ($scope.stats[containerId].image.includes('droneapiserver')){
      $scope.serverAPIIndex.push(containerId);
    } else if  ($scope.stats[containerId].image.includes('droneapiworker')){
      $scope.workerAPIIndex.push(containerId);
    }
    else {
      $scope.utilityContainerIndex.push(containerId);
    }

    $scope.containers[containerId]={};
    $scope.containers[containerId].labels= ['','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','',''];
    $scope.containers[containerId].series= ['CPU','Memory'];
    $scope.containers[containerId].data=  [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]];
    $scope.containers[containerId].options= { animation:false, scaleOverride:true, scaleStepWidth: 50, scaleStartValue: 0, scaleSteps:10,   scaleBeginAtZero: true,
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
                  labelString: 'CPU (%)'
                },
                            ticks: {
                beginAtZero: true                            }
                        },{
              position: 'right',
              id: 'y-axis-2',
                            display: true,
              scaleLabel: {
                  display: true,
                  labelString: 'Memory (%)'
                },
                            ticks: {
                beginAtZero: true                            }
                        }]
    }
  };

  $scope.containers[containerId].datasetOverride = [{ yAxisID: 'y-axis-1' }, { yAxisID: 'y-axis-2' }];

  }

    //$scope.container.onClick= function (points, evt) {
    //    console.log(points, evt);
    //  };



  function getContainerStats() {
  $http.get('http://droneapi.ddns.net:4000/').
      then(function(data, status, headers, config) {
        console.log('getContainerStats API get success',data,status);
        //data has id, image, cpu
        //we want an array of the latest stat objects
        //$scope.stats.splice(0, $scope.stats.length);  //reset stats array to zero elements (without creating new array)
        if (data.data.containers.length>0){
          $scope.stats=[]; //delete every element from previous array
        }

        for(var statObj in data.data.containers) {
          var containerObj=data.data.containers[statObj];
          //console.log(containerObj);
          containerObj.id=containerObj.id.substring(0,6);
          $scope.stats[containerObj.id]=containerObj;
        }

        //console.log($scope.stats.length);
        //console.log($scope.stats);
        for(var stat in $scope.stats) {
          var statObj=$scope.stats[stat];

          if (!$scope.containers[statObj.id]) {
            //build new baseline
            addGraphBaseline(statObj.id);
          }
          $scope.containers[statObj.id].data[0].push(statObj.total_cpu);
          $scope.containers[statObj.id].data[1].push(statObj.total_memory);
          if ($scope.containers[statObj.id].data[0].length>80) {
            $scope.containers[statObj.id].data[0].shift();
          }
          if ($scope.containers[statObj.id].data[1].length>80) {
            $scope.containers[statObj.id].data[1].shift();
          }
        }

        //go through each container and check there are still stats for container
        for (var containerIndex in $scope.containers){


          var containerFound=false;
          for(var stat in $scope.stats) {
            var statObj=$scope.stats[stat];
            if (statObj.id==containerIndex){
              containerFound=true;
            }
          }

          if (!containerFound){
            //delete container
            //delete from whichever index it is in and the actual container
            for (var i in $scope.containerIndex){
              if ($scope.containerIndex[i]==containerIndex){
                $scope.containerIndex.splice(i,1);
              }
            }
            for (var i in $scope.proxyIndex){
              if ($scope.proxyIndex[i]==containerIndex){
                $scope.proxyIndex.splice(i,1);
              }
            }
            for (var i in $scope.utilityContainerIndex){
              if ($scope.utilityContainerIndex[i]==containerIndex){
                $scope.utilityContainerIndex.splice(i,1);
              }
            }
            for (var i in $scope.serverAPIIndex){
              if ($scope.serverAPIIndex[i]==containerIndex){
                $scope.serverAPIIndex.splice(i,1);
              }
            }
            for (var i in $scope.workerAPIIndex){
              if ($scope.workerAPIIndex[i]==containerIndex){
                $scope.workerAPIIndex.splice(i,1);
              }
            }
            delete $scope.containers[containerIndex];
          }
        }

      },
        function(data, status, headers, config) {
          // log error
          console.log('getContainerStats API get error',data, status, headers, config);
        });
      }

  $scope.$on('$destroy', function() {
    // clean up stuff
      console.log('###################################################');
      console.log('Unloading Performance Controller');
    $interval.cancel(statsTimer);
  })
  var statsTimer = $interval(getContainerStats, 2000);

  console.log('###################################################');
  console.log('Loading Performance Controller');

}]);
