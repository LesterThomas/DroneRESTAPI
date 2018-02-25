"""Thi module manages the Redis database including sentinel"""



import sys
import logging
import traceback
import json
import time
import math
import redis
from redis.sentinel import Sentinel
import droneAPIUtils


class RedisManager:

    def __init__(self):
        self.logger = logging.getLogger("DroneAPIWorker." + str(__name__))
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.info("droneAPIRedis Initialised redisManager")
        self.sentinelConnection=None
        return

    def get(self, inKey, default={}):
        try:
            self.logger.debug("droneAPIRedis:get")

            if self.sentinelConnection==None:
                self.logger.info("droneAPIRedis:get getting connection to redis sentinel")
                self.sentinelConnection = Sentinel([('redis-sentinel', 26379)], socket_timeout=0.1)

            self.logger.debug("droneAPIRedis:get getting redis master from sentinel")
            redisdB = self.sentinelConnection.master_for('mymaster', socket_timeout=0.1)

            output_str = redisdB.get(inKey)
            try:
                output = json.loads(output_str)
            except TypeError as ex:
                output=default
                redisdB.set(inKey, json.dumps(output))

            self.logger.debug("droneAPIRedis:get output = %s" , output)

        except Exception as ex:
            self.logger.warning("Exception in droneAPIRedis:get")
            self.logger.warning(ex)
            self.logger.warning("-----------------------------------------------------------------------")
            self.logger.warning("")
            self.sentinelConnection=None #reset connection to Sentinel
            time.sleep(1) #reduce the number of errors by rate-limiting redis connections
            raise Warning('Error connecting to Redis database')
        return output

    def set(self, inKey, inValue):
        try:
            self.logger.debug("droneAPIRedis:set")

            if self.sentinelConnection==None:
                self.logger.info("droneAPIRedis:get getting connection to redis sentinel")
                self.sentinelConnection = Sentinel([('redis-sentinel', 26379)], socket_timeout=0.1)

            self.logger.debug("droneAPIRedis:get getting redis master from sentinel")
            redisdB = self.sentinelConnection.master_for('mymaster', socket_timeout=0.1)

            redisdB.set(inKey, json.dumps(inValue))

        except Exception as ex:
            self.logger.warning("Exception in droneAPIRedis:set")
            self.logger.warning(ex)
            self.logger.warning("-----------------------------------------------------------------------")
            self.logger.warning("")
            self.sentinelConnection=None #reset connection to Sentinel
            time.sleep(1) #reduce the number of errors by rate-limiting redis connections
            raise Warning('Error connecting to Redis database')
        return

