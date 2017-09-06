"""This module provides the API endpoint to administer the API service."""


import logging
import traceback
import json
import uuid
import APIServerUtils
import requests
import web

my_logger = logging.getLogger("DroneAPIServer." + str(__name__))


class User:

    def __init__(self):
        return

    def POST(self):
        # This handles the HTTP POST request and creates a new user in the
        # database (or updates existing one if the user is already registered)
        try:
            my_logger.info("User POST method")
            APIServerUtils.applyHeadders()

            dataStr = web.data()
            my_logger.info(dataStr)
            data = json.loads(dataStr)

            user = APIServerUtils.redisdB.get("user:" + data["id_provider"] + ":" + str(data["id"]))

            if user:
                my_logger.info("User found: %s", user)
                user = json.loads(user)
            else:
                my_logger.info("User not found - creating new user")
                user = data
                uuidVal = uuid.uuid4()
                api_key = str(uuidVal)[:16]
                user["api_key"] = api_key
                APIServerUtils.redisdB.set("user:" + user["id_provider"] + ":" + str(user["id"]), json.dumps(user))
                APIServerUtils.redisdB.set("api_key:" + user["api_key"],
                                           json.dumps({"api_key": user["api_key"],
                                                       "user": user["id_provider"] + ":" + str(user["id"])}))

            my_logger.info("Return:%s", json.dumps(user))
        except Exception as e:
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": e.message, "args": e.args, "traceback": traceLines})
        return json.dumps(user)

    def OPTIONS(self):
        """This method handles the OPTIONS HTTP verb, required for CORS support."""
        try:
            my_logger.info("OPTIONS")
            # just here to support the CORS Cross-Origin security
            APIServerUtils.applyHeadders()

            outputObj = {}
            output = json.dumps(outputObj)
            my_logger.info("Return: =" + output)
        except Exception as e:
            my_logger.exception(e)
            tracebackStr = traceback.format_exc()
            traceLines = tracebackStr.split("\n")
            return json.dumps({"error": "An unknown Error occurred ", "details": e.message, "args": e.args, "traceback": traceLines})
        return output
