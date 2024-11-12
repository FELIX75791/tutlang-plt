#!/bin/bash

# Check if an input file (.tut) is provided
if [ -z "$1" ]; then
    echo "Usage: ./tut_parser.sh [input_file.tut]"
    exit 1
fi

# Check if the input file exists
if [ ! -f "$1" ]; then
    echo "Error: File '$1' not found!"
    exit 1
fi

# Run the lexer to generate tokens and save them to tokens.txt
echo "Running lexer on $1..."
python3 scanner.py "$1" > tokens.txt

# Check if lexer execution was successful by checking tokens.txt
if [ ! -s tokens.txt ]; then
    echo "Error: Lexer failed to generate tokens or empty output."
    rm tokens.txt
    exit 1
fi

echo "Lexer execution complete. Tokens saved to tokens.txt."

# Run the parser using the generated tokens
echo "Running parser on tokens.txt..."
python3 parser.py tokens.txt

# Clean up the temporary tokens file after parsing
rm tokens.txt

echo "Parser execution complete."
