#!/bin/bash

echo "Loading environment variables."
source .env

BUILD_CMD="docker build -t newman ."

echo "Running: $BUILD_CMD"
eval $BUILD_CMD

CMD="docker run -i -e AWS_ACCESS_KEY_ID=\"$AWS_ACCESS_KEY\" \
    -e AWS_SECRET_ACCESS_KEY=\"$AWS_SECRET_KEY\" \
    -e NEWMAN_CRON=\"$NEWMAN_CRON\" \
    -v \"$(pwd):/newman\" \
    newman \
    bash -c \"cp -r /newman/ deploy_folder/ && \
              cd /deploy_folder/ && \
              pip install -r requirements.txt -t . && \
              npm install && npm run deploy ${STAGE:=prod} \
              \"
    "

echo "Running: $CMD"
eval $CMD
