# Apply this after starting the other kubernetes manifests.
# This script adds slave redis databases and redis sentinels.

# Create a replication controller for redis servers
kubectl create -f kubernetesManifests/individualManifestFiles/redis-controller.yaml

# Create a replication controller for redis sentinels
kubectl create -f kubernetesManifests/individualManifestFiles/redis-sentinel-controller.yaml

sleep 5

# Scale both replication controllers
kubectl scale rc redis --replicas=3
kubectl scale rc redis-sentinel --replicas=3
