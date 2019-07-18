#!/bin/bash

# Easy life
echo 'Starting Mongo'
sudo service mongod start

echo 'running bot'
./TelegramBot.py
