#!/usr/bin/env bash
# Install Chromium and Chromedriver
apt-get update && apt-get install -y chromium chromium-driver

# Install python dependencies
pip install -r requirement.txt
