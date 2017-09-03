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


        getDockerStats:function(inScope) {
            $http.get("http://localhost:4000/stats")
                .success(function (response) {
                    var index;
                    var containerIndex;
                    //alert(inScope.cpuLineArray.length);

                    //put the stats data in the response object into the correct container.
                    //assess whether any container has reached its max or min cpu limit.
                    for (index=0;index<response.length;index++){
                        for (containerIndex=0;containerIndex<inScope.console.containers.length;containerIndex++){
                            if (response[index].id.localeCompare(inScope.console.containers[containerIndex].line.id)==0) {
                                inScope.console.containers[containerIndex].line.data[0].push(Math.round(response[index].cpu));

                                if (inScope.console.containers[containerIndex].line.data[0].length>40) {
                                   inScope.console.containers[containerIndex].line.data[0].shift();
                                }
                            }       
                        }    
                    }  

            	});
        	}
        };
    });

