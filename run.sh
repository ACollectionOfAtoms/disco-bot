docker build -t disco-bot .
docker run --env-file env.list -d disco-bot
