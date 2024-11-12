# TutLang

## Author
Ziyue Jin (zj2393)

## Introduction
TutLang is a minimalist general-purpose programming language. The primary focus of TutLang is
simplicity and ease of learning, targeting novice programmers or those interested in creating highly
readable code. The syntax will be intentionally limited to basic constructs like variable assignment,
conditional statements (if, else), loops (while, loop), and mathematical operations (+, -, *). Additionally,
the language will support function definitions (def), making it capable of modular programming.

## Installation and Execution Steps

### Build the Docker Image

```bash
docker build -t tutlang .
```

### Run Docker Container

```bash
docker run -it --rm -v $(pwd):/usr/src/app tutlang
```

### Execute the Lexer Only

```./tut_lexer.sh [input_file.tut]```

Five examples are given in the `./examples_lexer` folder, and the expected outputs are in the file `./examples_lexer/expected_output.txt` Examples 1-3 shows the normal situation where the output is a valid AST, whereas examples 4-5 shows the error handling capabilities of the lexer.

### Execute the Parser (Automatically Calls Lexer)

```./tut_parser.sh [input_file.tut]```

The parser will first call lexer to give the token list of the input_file, then run parser to give the AST. So you dont have to run lexer first before run parser and thus simplify the steps.

Eight examples are given in the `./examples_parser` folder, and the expected outputs are in the file `./examples_parser/expected_output.txt`. Examples 1-4 shows the normal situation where the output is a valid AST, whereas examples 5-8 shows the error handling capabilities of the parser.


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

## Context-Free Grammar (CFG) for the Language

### Non-Terminals
- `Program`
- `Statement`
- `Declaration`
- `Assignment`
- `IfStatement`
- `DoUntilStatement`
- `LoopStatement`
- `OutputStatement`
- `Function`
- `ParameterList`
- `ReturnStatement`
- `Block`
- `Condition`
- `Expression`
- `Term`
- `Factor`

### Terminals
- **Keywords**: `declare`, `def`, `if`, `else`, `do`, `until`, `loop`, `output`, `return`
- **Identifiers**: `IDENTIFIER`
- **Operators**: `<-`, `==`, `!=`, `<`, `>`, `<=`, `>=`, `+`, `-`, `*`, `/`
- **Literals**: `INTLITERAL`, `STRINGLITERAL`
- **Symbols**: `(`, `)`, `{`, `}`, `,`

### Rules
```
Program → Statement Program | ε

Statement → Declaration | Assignment | IfStatement | DoUntilStatement | LoopStatement | OutputStatement | Function | ReturnStatement

Declaration → declare IDENTIFIER <- Expression

Assignment → IDENTIFIER <- Expression

IfStatement → if ( Condition ) Block ElseClause  
ElseClause → else Block | ε

DoUntilStatement → do Block until Condition

LoopStatement → loop Expression Block

OutputStatement → output STRINGLITERAL

Function → def IDENTIFIER ( ParameterList ) Block

ParameterList → IDENTIFIER ParameterListTail | ε  
ParameterListTail → , IDENTIFIER ParameterListTail | ε

ReturnStatement → return Expression

Block → { StatementList }  
StatementList → Statement StatementList | ε

Condition → Expression RelationalOp Expression  
RelationalOp → == | != | < | > | <= | >=

Expression → Term ExpressionTail  
ExpressionTail → + Term ExpressionTail | - Term ExpressionTail | ε

Term → Factor TermTail  
TermTail → * Factor TermTail | / Factor TermTail | ε

Factor → IDENTIFIER | INTLITERAL | STRINGLITERAL | ( Expression )
```