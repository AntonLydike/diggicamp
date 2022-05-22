#!/usr/bin/env bash

chown -R $FILES_USER:$FILES_GROUP /data

while :; do
  dgc-timer
  sleep 1m
done