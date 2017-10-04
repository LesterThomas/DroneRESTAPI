"""The Main module of the docker performance monitoring service. """
#!/usr/bin/env python

# Import external modules
import time
import json
import traceback
import os
import docker
import web


# Import  modules that are part of this app

def applyHeadders():
    web.header('Content-Type', 'application/json')
    web.header('Access-Control-Allow-Origin', '*')
    web.header('Access-Control-Allow-Credentials', 'true')
    web.header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
    web.header('Access-Control-Allow-Headers', 'Content-Type')
    return

class CatchAll(object):
    """THis class handles any  URLs for the API."""

    def GET(self,inVal):  # pylint: disable=R0201
        """THis method handles any unknown GET URL requests for the API."""
        try:
            applyHeadders()
            output_obj = {}
            docker_host_ip=os.environ['DOCKER_HOST_IP']
            print("Getting containers from Docker Host")


            docker_client = docker.DockerClient(
            version='1.27',
            base_url='tcp://' + docker_host_ip + ':4243')  # docker.from_env(version='1.27')

            #result = requests.get('http://'+ docker_host_ip + ":4243/v1.24/containers/json")
            container_array=docker_client.containers.list()

            #container_array=json.loads(result.text)
            output={"containers":[]}
            for  container in container_array:
                print(str(container.image)[9:-2])

                #perfData = requests.get('http://'+ docker_host_ip + ":4243/v1.24/containers/"+container['Id']+"/top?ps_args=aux")
                #performance_obj=json.loads(perfData.text)
                perf_output={"processes":[]}
                total_cpu=0
                total_memory=0
                performance_obj=container.top(ps_args="aux")
                for process in performance_obj['Processes']:
                    perf_output['processes'].append({"pid":process[1],"cpu":process[2],"memory":process[3],"command":process[10]})
                    total_cpu=total_cpu+float(process[2])
                    total_memory=total_memory+float(process[3])
                output['containers'].append({"image":str(container.image),"id":container.id,"perf":perf_output,"total_cpu":round(total_cpu,1),"total_memory":round(total_memory,1)})


        except Exception as ex:  # pylint: disable=W0703
            print(ex)
            traceback_str = traceback.format_exc()
            trace_lines = traceback_str.split("\n")
            return json.dumps({"error": "An unknown Error occurred ",
                               "details": ex.message,
                               "args": ex.args,
                               "traceback": trace_lines})
        return json.dumps(output)


##########################################################################
# startup
##########################################################################


def startup():
    """This function starts the web
    application that serves the API HTTP traffic."""


    # set API url endpoints and class handlers. Each handler class is in its
    # own python module
    urls = (
        '/(.*)', 'CatchAll'
    )

    # start API web application server
    webApp = web.application(urls, globals())
    webApp.run()

    return


if __name__ == "__main__":
    print("Starting dockerperf at " + str(time.time()))
    startup()
