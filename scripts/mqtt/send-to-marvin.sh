#!/bin/bash
# Send message to Marvin via MQTT
# Usage: send-to-marvin.sh "Your message here"

cd /home/magi/clawd/scripts/mqtt
BOT_NAME=magi node send.js marvin ""
