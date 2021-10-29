docker ps | awk '{ print $1,$2 }' | grep disco-bot | awk '{print $1 }' | xargs -I {} docker stop {}
docker ps -a | awk '{ print $1,$2 }' | grep disco-bot | awk '{print $1 }' | xargs -I {} docker rm {}
docker build -t disco-bot .
docker run --restart unless-stopped --env-file env.list -d disco-bot
