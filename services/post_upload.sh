#!/bin/bash
if systemctl stop chat_bot.service ; then
    sudo cp /home/ubuntu/chat_bot/services/chat_bot.service /etc/systemd/system/
else
    echo "No chat_bot.service found in system, now will creating"
    sudo cp /home/ubuntu/chat_bot/services/chat_bot.service /etc/systemd/system
fi
sudo systemctl daemon-reload
sudo systemctl enable chat_bot.service
sudo systemctl start chat_bot.service
rm  /home/ubuntu/chat_bot.tar