docker run -d --restart="always" --name redis -p 6379:6379 redis
sleep 10
docker run -d --restart="always" --link redis:redis -p 8081:8081 tenstartups/redis-commander --redis-host redis

