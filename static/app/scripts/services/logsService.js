'use strict';
/**
 * @ngdoc function
 * @name sbAdminApp.controller:MainCtrl
 * @description
 * # MainCtrls
 * Controller of the sbAdminApp
 */


//**********************NOT USED**********

var adminApp = angular.module('droneFrontendApp');

/**
 * The `logsService` service stores details from the Docker logging.
 *
  */
adminApp.service('logsService',     function($http) {
  
    this.logger = { 
        
        events:[  {image:'fa-upload', text:'Admin console started', time: (new Date).toLocaleTimeString()} ],  //events shown on the dashboard page
        logs:[],
        line : {
            labels: ['','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','',''],
            series: ['Hits'],
            data:  [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],
            options: { animation:false, scaleOverride:true, scaleStepWidth: 50, scaleStartValue: 0, scaleSteps:10 },
              onClick: function (points, evt) {
              console.log(points, evt);
                }
            },

        addEvent:function(inEventObject) {
        	this.events.unshift(inEventObject);
        	if (this.events.length>20) {
        		this.events.pop();
            	}
            },



        getDockerLogs: function(inScope) {
            $http.get("http://localhost:4000/logs")
                .success(function (response) {
                    inScope.logger.logs.splice(0, inScope.logger.logs.length);  //reset logs array to zero elements (without creating new array)
                    
                    for (var index=0;index<response.length;index++){
                        if ((response[index].image==inScope.console.ZTUAContainer) || (response[index].image==inScope.console.ZTUBContainer)) {
                                inScope.logger.logs.push(response[index]);
                        }       
                    }
                    //alert(inScope.logger.logs.length);
                    inScope.logger.line.data[0].push(inScope.logger.logs.length);
                    
                });
        
            if (inScope.logger.line.data[0].length>40) {
               inScope.logger.line.data[0].shift();
                }
            },

        getDockerStats:function(inScope) {
            $http.get("http://localhost:4000/stats")
                .success(function (response) {
                    var index;
                    var containerIndex;
                    var maxCPUReached=false;
                    var minCPUReached=false;
                    //alert(inScope.cpuLineArray.length);

                    //put the stats data in the response object into the correct container.
                    //assess whether any container has reached its max or min cpu limit.
                    for (index=0;index<response.length;index++){
                        for (containerIndex=0;containerIndex<inScope.console.containers.length;containerIndex++){
                            if (response[index].id.localeCompare(inScope.console.containers[containerIndex].line.id)==0) {
                                inScope.console.containers[containerIndex].line.data[0].push(Math.round(response[index].cpu));

                                //ass whether max or min CPU level is reached for this container.
                                if (response[index].cpu>90) {
                                    maxCPUReached=true;
                                };
                                if (response[index].cpu<10) {
                                    minCPUReached=true;
                                };
                                if (inScope.console.containers[containerIndex].line.data[0].length>40) {
                                   inScope.console.containers[containerIndex].line.data[0].shift();
                                }
                            }       
                        }    
                    }  
                    //if authScale is switched on, ajust the target number of instances based on the max and min cpu
                    if (inScope.console.autoScale){
                        //auto-scale
                        if (maxCPUReached) {
                            inScope.console.maxCPUSeconds++;
                            inScope.console.minCPUSeconds=0;
                            if (inScope.console.maxCPUSeconds>3) { //if max CPU for more than 3 seconds then scale up
                                inScope.console.instances=inScope.console.instances+1;
                                inScope.console.maxCPUSeconds=-2;  //allow 2 seconds for new container to start
                            //alert(inScope.console.instances);
                             }
                        } else {
                            inScope.console.maxCPUSeconds=0;
                        }
                        if (minCPUReached) {
                            inScope.console.minCPUSeconds++;
                            inScope.console.maxCPUSeconds=0;
                            if (inScope.console.minCPUSeconds>6) { //if min CUP for more than 6 seconds then scale down
                                if (inScope.console.instances>2) {
                                    inScope.console.instances=inScope.console.instances-1;
                                    inScope.console.minCPUSeconds=-2; //allow 2 seconds for container to stop
                                }
                            //alert(inScope.console.instances);
                             }
                        } else {
                            inScope.console.minCPUSeconds=0;
                        }
                    }
            	});
        	}
        };
    });

