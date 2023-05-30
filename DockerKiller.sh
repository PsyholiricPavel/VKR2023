docker rm $(docker ps -a -q)
docker rmi $(docker images -q)
docker network rm $(docker network ls -q)
docker volume rm $(docker volume ls -q)
