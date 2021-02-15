docker stop $(docker ps -aq)
docker system prune -f
docker build -t disco-bot .
docker run --restart unless-stopped --env-file env.list -d disco-bot
