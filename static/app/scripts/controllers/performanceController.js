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
  $scope.mainAPIIndex=[];

  function addGraphBaseline(containerId){
  
    if ($scope.stats[containerId].image.includes('dronesim')){
      $scope.containerIndex.push(containerId);
    }
    else if ($scope.stats[containerId].image.includes('droneproxy')){
      $scope.proxyIndex.push(containerId);
    } else if  ($scope.stats[containerId].image.includes('droneapi')){
      $scope.mainAPIIndex.push(containerId);  
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
                beginAtZero: true,
                                steps: 10,
                                stepValue: 10,
                                max: 100
                            }
                        },{
              position: 'right',
              id: 'y-axis-2',
                            display: true,
              scaleLabel: {
                  display: true,
                  labelString: 'Memory (%)'
                },
                            ticks: {
                beginAtZero: true,
                                steps: 10,
                                stepValue: 10,
                                max: 100
                            }
                        }]
    }
  };
  
  $scope.containers[containerId].datasetOverride = [{ yAxisID: 'y-axis-1' }, { yAxisID: 'y-axis-2' }];

  }
  
    //$scope.container.onClick= function (points, evt) {
    //    console.log(points, evt);
    //  };



  function getContainerStats() {
  $http.get('http://localhost:4000/stats').
      then(function(data, status, headers, config) {
        console.log('getContainerStats API get success',data,status); 
        //data has id, image, cpu
        //we want an array of the latest stat objects
        //$scope.stats.splice(0, $scope.stats.length);  //reset stats array to zero elements (without creating new array)
        for(var statObj in data.data) {
          var containerObj=data.data[statObj];
          //console.log(containerObj); 
          $scope.stats[containerObj.id]=containerObj;
        }
        //console.log($scope.stats.length); 
        //console.log($scope.stats); 
        for(var stat in $scope.stats) {
          var statObj=$scope.stats[stat];
          console.log(statObj.image, statObj.cpu); 

          if (!$scope.containers[statObj.id]) {
            //build new baseline
            addGraphBaseline(statObj.id);
          }


          $scope.containers[statObj.id].data[0].push(statObj.cpu);
          if ($scope.containers[statObj.id].data[0].length>80) {
            $scope.containers[statObj.id].data[0].shift();
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
  var statsTimer = $interval(getContainerStats, 1000);

  console.log('###################################################'); 
  console.log('Loading Performance Controller'); 

}]);
