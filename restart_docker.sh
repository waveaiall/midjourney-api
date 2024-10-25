#!/bin/bash

image_version=$(sudo docker image ls|grep learn2pro/midjourney-api|tail -n +2|head -n 1|awk -F ' ' '{print $2}'|cut -f2 -d '.')
incr_number=$(($image_version+1))
new_version="0."$incr_number".0"

echo 'start build docker with new version=>'$new_version

sudo docker build -t learn2pro/midjourney-api:$new_version .

echo 'build done'

ps_id=$(sudo docker ps|grep mj-server|tail -n +1|cut -f1 -d ' ')

echo 'stop=>'$ps_id'and restart with new version=>'$new_version

if [ -z "$ps_id" ]; then
    echo "No running container found. Skipping stop operation."
else
    sudo docker stop $ps_id
fi

bot_ps_id=$(sudo docker ps|grep mj-bot|tail -n +1|cut -f1 -d ' ')

echo 'stop=>'$bot_ps_id'and restart with new version=>'$new_version

if [ -z "$bot_ps_id" ]; then
    echo "No running container found. Skipping stop operation."
else
    sudo docker stop $bot_ps_id
fi

echo '------------------------>start mj-server------------------------>'


# docker network create mjapi

sudo docker run -d --net mjapi --name mj-server -p 8062:8062 \
	-e TZ=Asia/Shanghai \
	-e LOG_LEVEL=DEBUG \
    -e USER_TOKEN="NzEwNDY0NTA4Mjc1MDY0OTAy.GkM6DD.9t2VUL2SW3FNmH4Mkt2Lw-mGAHtYJvoys41EyU" \
	-e GUILD_ID="1298890119646023690" \
	-e CHANNEL_ID="1298890119646023693" \
	-e CONCUR_SIZE=3 \
	-e WAIT_SIZE=10 \
	learn2pro/midjourney-api:$new_version

echo '------------------------>start mj-bot------------------------>'
sudo docker run -d --net mjapi --name mj-bot \
	-e TZ=Asia/Shanghai \
	-e LOG_LEVEL=DEBUG \
    -e USER_TOKEN="NzEwNDY0NTA4Mjc1MDY0OTAy.GkM6DD.9t2VUL2SW3FNmH4Mkt2Lw-mGAHtYJvoys41EyU" \
	-e BOT_TOKEN="MTI5ODg1NzczNjkwNTQyOTAwMw.Gr8MiT.wai6TlLIVkVaL180bsj3BmIYAWOs1xvH-BV2Rs" \
	-e GUILD_ID="1298890119646023690" \
	-e CHANNEL_ID="1298890119646023693" \
	-e CALLBACK_URL="http://mj-server:8062/v1/api/trigger/midjourney/callback" \
	-e QUEUE_RELEASE_API="http://mj-server:8062/v1/api/trigger/queue/release" \
	learn2pro/midjourney-api:$new_version

echo 'restart done'

echo '------------------------>logs of new container------------------------>'
new_ps_id=$(sudo docker ps|grep mj-server|tail -n +1|cut -f1 -d ' ')

sudo docker logs $new_ps_id -f