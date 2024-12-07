#!/bin/bash

# Usage: ./tut_compiler.sh <source_file.tut> [--debug] [--exec]

SOURCE_FILE=$1
DEBUG="false"
EXEC="false"

# Check for flags
for arg in "$@"; do
  if [ "$arg" == "--debug" ]; then
    DEBUG="true"
  elif [ "$arg" == "--exec" ]; then
    EXEC="true"
  fi
done

# Check if source file is provided
if [ -z "$SOURCE_FILE" ]; then
  echo "Usage: ./tut_compiler.sh <source_file.tut> [--debug] [--exec]"
  exit 1
fi

# Extract the base name (without extension)
BASE_NAME=$(basename "$SOURCE_FILE" .tut)

# Define file names
TOKENS_FILE="$BASE_NAME.tokens"
AST_FILE="$BASE_NAME.ast"
OUTPUT_PYTHON_FILE="$BASE_NAME.py"

# Step 1: Run Scanner
if [ "$DEBUG" == "true" ]; then
  echo "Running scanner..."
fi
python3 scanner.py "$SOURCE_FILE" > "$TOKENS_FILE"
if [ $? -ne 0 ]; then
  echo "Scanner failed. Exiting."
  exit 1
fi
if [ "$DEBUG" == "true" ]; then
  echo "Tokens generated in $TOKENS_FILE"
fi

# Step 2: Run Parser
if [ "$DEBUG" == "true" ]; then
  echo "Running parser..."
fi
python3 parser.py "$TOKENS_FILE" > "$AST_FILE"
if [ $? -ne 0 ]; then
  echo "Parser failed. Exiting."
  exit 1
fi
if [ "$DEBUG" == "true" ]; then
  echo "AST generated in $AST_FILE"
fi

# Step 3: Run Code Generator
if [ "$DEBUG" == "true" ]; then
  echo "Running code generator..."
fi
python3 code_generator.py "$AST_FILE" "$OUTPUT_PYTHON_FILE"
if [ $? -ne 0 ]; then
  echo "Code generation failed. Exiting."
  exit 1
fi

# Only print the following in normal mode:
if [ "$DEBUG" != "true" ]; then
  echo "$OUTPUT_PYTHON_FILE generated!"
else
  echo "Python code generated in $OUTPUT_PYTHON_FILE"
fi

# Step 4: Execute Generated Code (Optional)
if [ "$EXEC" == "true" ]; then
  echo "--exec flag used, executing generated Python code..."
  echo "----------------------results-----------------------"
  python3 "$OUTPUT_PYTHON_FILE"
  echo "---------------------end results--------------------"
fi

# Step 5: Clean up intermediate files (if not in debug mode)
if [ "$DEBUG" != "true" ]; then
  rm -f "$TOKENS_FILE" "$AST_FILE"
else
  echo "Debug mode enabled. Intermediate files retained."
fi
