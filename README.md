# TutLang

## Author
Ziyue Jin (zj2393)

## Introduction
TutLang is a minimalist general-purpose programming language. The primary focus of TutLang is
simplicity and ease of learning, targeting novice programmers or those interested in creating highly
readable code. The syntax will be intentionally limited to basic constructs like variable assignment,
conditional statements (if, else), loops (while, loop), and mathematical operations (+, -, *). Additionally,
the language will support function definitions (def), making it capable of modular programming.


## Lexical Grammar
1. **KEYWORD**: `"declare" | "def" | "if" | "else" | "do" | "until" | "loop" | "return" | "output"`
2. **OPERATOR**: `"<-" | "==" | "!=" | "<=" | ">=" | "<" | ">" | "+" | "-" | "*" | "/"`
3. **INTLITERAL**: `[0-9]+`
4. **IDENTIFIER**: `[a-zA-Z][_a-zA-Z0-9]*`
5. **STRINGLITERAL**: `\"[^\"]*\"`
6. **LPAR**: `"("`
7. **RPAR**: `")"`
8. **LBRACE**: `"{"`
9. **RBRACE**: `"}"`
10. **COMMA**: `","`
11. **WHITESPACE**: `\s+`

## Installation/Execution Step

Build the Docker Image

```docker build -t tutlang-lexer .```

Run Docker container:

```docker run -it --rm -v $(pwd):/usr/src/app tutlang-lexer```

Execute the Lexer

```./tut_lexer.sh [input_file.tut]```

Five examples are given in the `./examples` folder, and the expected outputs are in the file `./examples/expected_output.txt`
