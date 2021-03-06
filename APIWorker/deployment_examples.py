# Copyright 2016 The Kubernetes Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from os import path

import time
import yaml

from kubernetes import client, config



def create_deployment_object(inName):
    # Configureate Pod template container
    container = client.V1Container(
        name=inName,
        image="nginx:1.7.9",
        ports=[]) #[client.V1ContainerPort(container_port=80)])
    # Create and configurate a spec section
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": inName}),
        spec=client.V1PodSpec(containers=[container]))
    # Create the specification of deployment
    spec = client.ExtensionsV1beta1DeploymentSpec(
        replicas=1,
        template=template)
    # Instantiate the deployment object
    deployment = client.ExtensionsV1beta1Deployment(
        api_version="extensions/v1beta1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name=inName),
        spec=spec)

    return deployment


def create_deployment(api_instance, deployment, inName):
    # Create deployement
    api_response = api_instance.create_namespaced_deployment(
        body=deployment,
        namespace="default")
    print("Deployment created. status='%s'" % str(api_response.status))


def update_deployment(api_instance, deployment, inName):
    # Update container image
    deployment.spec.template.spec.containers[0].image = "nginx:1.9.1"
    # Update the deployment
    api_response = api_instance.patch_namespaced_deployment(
        name=inName,
        namespace="default",
        body=deployment)
    print("Deployment updated. status='%s'" % str(api_response.status))


def delete_deployment(api_instance, inName):
    # Delete deployment
    api_response = api_instance.delete_namespaced_deployment(
        name=inName,
        namespace="default",
        body=client.V1DeleteOptions(
            propagation_policy='Foreground',
            grace_period_seconds=5))
    print("Deployment deleted. status='%s'" % str(api_response.status))


def main():
    # Configs can be set in Configuration class directly or using helper
    # utility. If no argument provided, the config will be loaded from
    # default location.
    config.load_incluster_config()
    extensions_v1beta1 = client.ExtensionsV1beta1Api()
    # Create a deployment object with client-python API. The deployment we
    # created is same as the `nginx-deployment.yaml` in the /examples folder.
    print "creating 5 deployments"
    for i in range(2):
        deploymentName="lester" + str(i)
        print("deployment name %s",deploymentName)
        deployment = create_deployment_object(deploymentName)
        create_deployment(extensions_v1beta1, deployment,deploymentName)
    time.sleep(20)

    print "updating 5 deployments"
    for i in range(2):
        deploymentName="lester" + str(i)
        print("deployment name %s",deploymentName)
        deployment = create_deployment_object(deploymentName)
        update_deployment(extensions_v1beta1, deployment,deploymentName)
    time.sleep(20)

    print "deleting 5 deployments"
    for i in range(2):
        deploymentName="lester" + str(i)
        print("deployment name %s",deploymentName)
        deployment = create_deployment_object(deploymentName)
        delete_deployment(extensions_v1beta1,deploymentName)




if __name__ == '__main__':
    main()
