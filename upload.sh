#!/bin/bash

for file in Portal*; do
    if [ -f "$file" ]; then
        python3 current.py $file | curl -H "Content-Type: application/json"  -X POST -d "$(</dev/stdin)" http://$1:3333/current
        sleep 1
    fi
done
python3 forecast.py forecast.json | curl -H "Content-Type: application/json"  -X POST -d "$(</dev/stdin)" http://$1:3333/forecast
