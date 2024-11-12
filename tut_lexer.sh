#!/bin/bash

# Check if an argument (input file) is provided
if [ -z "$1" ]; then
    echo "Usage: ./tut_lexer.sh [input_file.tut]"
    exit 1
fi

# Check if the input file exists
if [ ! -f "$1" ]; then
    echo "Error: File '$1' not found!"
    exit 1
fi

# Run the lexer Python script with the input file
python3 scanner.py "$1"

# Notify the user of successful execution
echo "Lexer execution complete."
