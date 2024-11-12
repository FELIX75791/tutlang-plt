# TutLang

## Author
Ziyue Jin (zj2393)

## Introduction
TutLang is a minimalist general-purpose programming language. The primary focus of TutLang is
simplicity and ease of learning, targeting novice programmers or those interested in creating highly
readable code. The syntax will be intentionally limited to basic constructs like variable assignment,
conditional statements (if, else), loops (while, loop), and mathematical operations (+, -, *). Additionally,
the language will support function definitions (def), making it capable of modular programming.




## Installation/Execution Step

Build the Docker Image

```docker build -t tutlang-lexer .```

Run Docker container:

```docker run -it --rm -v $(pwd):/usr/src/app tutlang-lexer```

Execute the Lexer

```./tut_lexer.sh [input_file.tut]```

Execute the Parser

```./tut_parser.sh [input_file.tut]```

The parser will first call lexer to give the token list of the input_file, then run parser to give the AST.

Five examples are given in the `./examples` folder, and the expected outputs are in the file `./examples/expected_output.txt`

## Lexer

### Lexical Grammar
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

## Parser

### Context Free Grammar (CFG)
```
Program          -> StatementList

StatementList    -> Statement StatementList | ε

Statement        -> Declaration 
                 | Function 
                 | Assignment 
                 | ControlStatement 
                 | OutputStatement 
                 | ReturnStatement

Declaration      -> "declare" IDENTIFIER "<-" Expression

Function         -> "def" IDENTIFIER "(" ParameterList ")" Block

Assignment       -> IDENTIFIER "<-" Expression

ControlStatement -> IfStatement 
                 | DoUntilStatement 
                 | LoopStatement

IfStatement      -> "if" "(" Condition ")" Block ElseClause

ElseClause       -> "else" Block | ε

DoUntilStatement -> "do" Block "until" Condition

LoopStatement    -> "loop" Expression Block

OutputStatement  -> "output" STRINGLITERAL

ReturnStatement  -> "return" Expression

Condition        -> Expression RelationalOp Expression

Expression       -> Term Expression'

Expression'      -> ("+" | "-") Term Expression' | ε

Term             -> Factor Term'

Term'            -> ("*" | "/") Factor Term' | ε

Factor           -> IDENTIFIER 
                 | INTLITERAL 
                 | STRINGLITERAL 
                 | "(" Expression ")"

Block            -> "{" StatementList "}"

ParameterList    -> IDENTIFIER ParameterList'

ParameterList'   -> "," IDENTIFIER ParameterList' | ε

RelationalOp     -> "==" | "!=" | "<=" | ">=" | "<" | ">"
```

### LL(1) Parsing Table

| Non-terminal      | declare                    | def                        | IDENTIFIER                | if                             | do                             | loop                           | output                         | return                         | `{`                            | `(`                            | INTLITERAL                    | STRINGLITERAL                  | `,`                           | `)`                           | `}`                           | ε           |
|-------------------|----------------------------|----------------------------|---------------------------|--------------------------------|--------------------------------|--------------------------------|--------------------------------|--------------------------------|--------------------------------|--------------------------------|--------------------------------|--------------------------------|--------------------------------|--------------------------------|--------------------------------|-------------|
| **Program**       | Program → StatementList    | Program → StatementList    | Program → StatementList   | Program → StatementList        | Program → StatementList        | Program → StatementList        | Program → StatementList        | Program → StatementList        | Program → StatementList        |                                  | Program → StatementList        |                                  |                                  |                                  |                                  | ε           |
| **StatementList** | StatementList → Statement StatementList | StatementList → Statement StatementList | StatementList → Statement StatementList | StatementList → Statement StatementList | StatementList → Statement StatementList | StatementList → Statement StatementList | StatementList → Statement StatementList | StatementList → Statement StatementList | ε              |                | StatementList → Statement StatementList |               |        |        | ε      | ε           |
| **Statement**     | Statement → Declaration    | Statement → Function       | Statement → Assignment    | Statement → ControlStatement   | Statement → ControlStatement   | Statement → ControlStatement   | Statement → OutputStatement    | Statement → ReturnStatement    |                                |                                |                                |                                |                                |                                |                                |             |
| **Declaration**   | Declaration → "declare" IDENTIFIER "<-" Expression |                            |                               |                                |                                |                                |                                |                                |                                |                                |                                |                                |                                |                                |                                |             |
| **Function**      |                            | Function → "def" IDENTIFIER "(" ParameterList ")" Block |                               |                                |                                |                                |                                |                                |                                |                                |                                |                                |                                |                                |                                |             |
| **Assignment**    |                            |                            | Assignment → IDENTIFIER "<-" Expression |                                |                                |                                |                                |                                |                                |                                |                                |                                |                                |                                |                                |             |
| **ControlStatement** |                          |                            |                               | ControlStatement → IfStatement | ControlStatement → DoUntilStatement | ControlStatement → LoopStatement |                                |                                |                                |                                |                                |                                |                                |                                |                                |             |
| **IfStatement**   |                            |                            |                               | IfStatement → "if" "(" Condition ")" Block ElseClause |                                |                                |                                |                                |                                |                                |                                |                                |                                |                                |                                |             |
| **ElseClause**    |                            |                            |                               |                                |                                |                                |                                |                                | ElseClause → "else" Block      |                                |                                |                                |                                | ε           | ε           | ε           |
| **DoUntilStatement** |                         |                            |                               |                                | DoUntilStatement → "do" Block "until" Condition |                                |                                |                                |                                |                                |                                |                                |                                |                                |                                |             |
| **LoopStatement** |                            |                            |                               |                                |                                | LoopStatement → "loop" Expression Block |                                |                                |                                |                                |                                |                                |                                |                                |                                |             |
| **OutputStatement** |                         |                            |                               |                                |                                |                                | OutputStatement → "output" STRINGLITERAL |                                |                                |                                |                                |                                |                                |                                |                                |             |
| **ReturnStatement** |                         |                            |                               |                                |                                |                                |                                | ReturnStatement → "return" Expression |                                |                                |                                |                                |                                |                                |                                |             |
| **Condition**     |                            |                            | Condition → Expression RelationalOp Expression |                                |                                |                                |                                |                                |                                | Condition → Expression RelationalOp Expression | Condition → Expression RelationalOp Expression | Condition → Expression RelationalOp Expression |                                |                                |                                |             |
| **Expression**    |                            |                            | Expression → Term Expression' |                                |                                |                                |                                |                                |                                | Expression → Term Expression' | Expression → Term Expression' | Expression → Term Expression' |                                |                                |                                |             |
| **Expression'**   | ε                          | ε                          | ε                           | ε                              | ε                              | ε                              | ε                              | ε                              | ε                              |                                | ε                              | ε                              |                                | ε                              | ε                              | ε           |
| **Term**          |                            |                            | Term → Factor Term'         |                                |                                |                                |                                |                                |                                | Term → Factor Term'            | Term → Factor Term'            | Term → Factor Term'            |                                |                                |                                |             |
| **Term'**         | ε                          | ε                          | ε                           | ε                              | ε                              | ε                              | ε                              | ε                              | ε                              |                                | ε                              | ε                              |                                | ε                              | ε                              | ε           |
| **Factor**        |                            |                            | Factor → IDENTIFIER         |                                |                                |                                |                                |                                |                                | Factor → "(" Expression ")"    | Factor → INTLITERAL            | Factor → STRINGLITERAL         |                                |                                |                                |             |
| **Block**         |                            |                            |                               |                                |                                |                                |                                |                                | Block → "{" StatementList "}"  |                                |                                |                                |                                |                                |                                |             |
| **ParameterList** | ParameterList → IDENTIFIER ParameterList' |                            |                               |                                |                                |                                |                                |                                |                                |                                |                                |                                | ParameterList → "," IDENTIFIER ParameterList' | ε           |             |             |
| 
