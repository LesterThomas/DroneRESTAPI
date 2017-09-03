# DroneRESTAPI - API Server

This is the stateless container that serves-up the API. It serves stateless end-points directly using the RedisDb; For stateful end-points, it queries the RedisDb for the correct worker container port and then delegates the API call to the worker.
