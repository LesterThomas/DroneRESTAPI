angular.module('droneFrontendApp')
.controller('NetworkCtrl', ['$scope', 'VisDataSet','droneService', function($scope, VisDataSet,droneService) {
	$scope.drones=droneService.drones;

	//if vehicle is disarmed then delete the authorized zone
	$scope.$watch("drones.collection", function (newValue) {		
		console.log("Drones collection",newValue);	
	    $scope.data = {"nodes":[
			{"id":"API Server","label":"API Server","size":40,"color":"#93D276","shape":"image","image":"images/server.jpg","shadow":true,"level":0}],
			"edges":[]};
			for (var droneIndex in $scope.drones.collection){
				var drone=$scope.drones.collection[droneIndex];
				if (drone.vehicleType=='simulated'){
					$scope.data.nodes.push({"id":drone.port,"label":"PORT: "+drone.port,"size":5,"color":"#1F1489","shape":"square","shadow":true,"level":20});
					$scope.data.nodes.push({"id":drone.name,"label":drone.name,"size":20,"color":"#7F8489","shape":"image","image":"images/dronesim.png","shadow":true,"level":100});
					$scope.data.edges.push({"from":drone.name,"to":drone.port});
					$scope.data.edges.push({"from":drone.port,"to":"API Server"});
				}
				if (drone.vehicleType=='real'){
					$scope.data.nodes.push({"id":drone.port,"label":"PORT: "+drone.port,"size":5,"color":"#1F1489","shape":"square","shadow":true,"level":20});
					$scope.data.nodes.push({"id":drone.name+" Proxy","label":"Proxy","size":20,"color":"#7F8489","shape":"image","image":"images/proxy.jpg","shadow":true,"level":33});
					$scope.data.nodes.push({"id":drone.droneConnectTo,"label":"PORT: "+drone.droneConnectTo,"size":5,"color":"#1F1489","shape":"square","shadow":true,"level":45});
					$scope.data.nodes.push({"id":drone.name,"label":drone.name,"size":20,"color":"#7F8489","shape":"image","image":"images/drone.png","shadow":true,"level":100});
					$scope.data.edges.push({"from":drone.port,"to":"API Server"});
					$scope.data.edges.push({"from":drone.name + " Proxy","to":drone.port});
					$scope.data.edges.push({"from":drone.name + " Proxy","to":drone.droneConnectTo});
					$scope.data.edges.push({"from":drone.name,"to":drone.droneConnectTo});
				}
			}

			/*,
			{"id":"DroneSim 1 PORT","label":"PORT: 14550","size":5,"color":"#1F1489","shape":"square","shadow":true,"level":20},
			{"id":"DroneSim 1","label":"DroneSim 1","size":20,"color":"#7F8489","shape":"image","image":"images/dronesim.png","shadow":true,"level":100},
			{"id":"DroneProxy 1 PORT B","label":"PORT: 14554","size":5,"color":"#1F1489","shape":"square","shadow":true,"level":20},
			{"id":"DroneProxy 1","label":"DroneProxy 1","size":20,"color":"#93D276","shape":"image","image":"images/proxy.jpg","shadow":true,"borderWidth":5,"level":1,"shadow.size":20,"level":33},
			{"id":"DroneProxy 1 PORT A","label":"PORT: 14553","size":5,"color":"#1F1489","shape":"square","shadow":true,"level":45},
			{"id":"RealDrone 1","label":"RealDrone 1","size":20,"color":"#7F8489","shape":"image","image":"images/drone.png","shadow":true,"level":100}, 
			{"id":"DroneSim 2 PORT","label":"PORT: 14551","size":5,"color":"#1F1489","shape":"square","shadow":true,"level":20},
			{"id":"DroneSim 2","label":"DroneSim 2","size":20,"color":"#7F8489","shape":"image","image":"images/dronesim.png","shadow":true,"level":100}
			],
			
			"edges":[
			{"from":"DroneProxy 1","to":"DroneProxy 1 PORT B","length":20},
			{"from":"DroneProxy 1","to":"DroneProxy 1 PORT A","length":20},
			{"from":"DroneProxy 1 PORT A","to":"RealDrone 1","length":200},
			{"from":"DroneProxy 1 PORT B","to":"API Server","length":200},
			{"from":"DroneSim 1","to":"DroneSim 1 PORT","length":10},
			{"from":"DroneSim 1 PORT","to":"API Server","length":100},
			{"from":"DroneSim 2","to":"DroneSim 2 PORT","length":10},
			{"from":"DroneSim 2 PORT","to":"API Server","length":100}
			]};		*/
	});



    $scope.onSelect = function(items) {
      // debugger;
      alert('select');
    };

    $scope.onClick = function(props) {
      //debugger;
      alert('Click');
    };

    $scope.onDoubleClick = function(props) {
      // debugger;
      alert('DoubleClick');
    };

    $scope.rightClick = function(props) {
      alert('Right click!');
      props.event.preventDefault();
    };

    $scope.options = {
		autoResize: true,
		height: '800',
		width: '100%',
		edges: {
			smooth: {
				type: 'dynamic',
				roundness: 0
			}
		},
		layout: {
			hierarchical: {
				direction: 'DU',
				levelSeparation:5
			}
		},
		physics:false
    };
	
    

  }
  
]);