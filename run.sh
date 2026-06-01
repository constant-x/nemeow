#!/bin/bash
echo "Starting processor"

if [ ! -d "inbox" ]; then
    echo "Error: inbox folder not found"
    exit 1
fi

python src/main.py
echo "Processing finished"