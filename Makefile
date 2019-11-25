#!/bin/bash

# Easy life
make:
	@echo 'Starting Mongo...'
	@eval 'sudo service mongod start'
	@echo 'starting bot...'
	./main.py
