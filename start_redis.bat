REM Apply this after starting the other kubernetes manifests.
REM This script adds slave redis databases and redis sentinels.

REM Create a replication controller for redis servers
kubectl create -f kubernetesManifests/individualManifestFiles/redis-controller.yaml

REM Create a replication controller for redis sentinels
kubectl create -f kubernetesManifests/individualManifestFiles/redis-sentinel-controller.yaml

timeout 5

REM Scale both replication controllers
kubectl scale rc redis --replicas=3
kubectl scale rc redis-sentinel --replicas=3
