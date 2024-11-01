
use crate::grammar::*;

// just your basic recursive decent parser
/*
expression -> literal | unary | binary | grouping ;
literal -> NUMBER | STRING; 
grouping -> "(" expression ")" ;
unary -> ( "-" | "!" ) expression;
bianry -> expression operator expression ;
operator -> "==" | "!=" | "<" | "<=" | ">" | ">=" | "+" | "-" | "*" | "/" ;
ARG_LIST -> expression ( "," ARG_LIST )?

expression -> term ;
term -> factor ( ( "-" | "+" ) factor )* ;  1 + 2 + 3 -> (1+1)+2
factor -> unary ( ( "/" | "*" ) unary )* ;
exponentaton -> unary "^"  exponentaton;
unary -> ( "!" | "-" ) unary | call ;
call -> primary "(" ARG_LIST ")"
primary -> NUMBER | STRING | "true" | "false" | "nil" | "(" expression ")" 

*/

pub fn parse(mut tokens: Vec<Token>) -> Result<Node, String> {
    expression(&mut tokens)
}

fn err(token: &Token, exprected: String) -> String {
    format!("Error: line {} exprected {} got '{}': ", token.line, exprected, token.lexeme)
}

fn err_no_token( exprected: String) -> String {
    format!("Exprected {}, got ''", exprected)
}


fn expression(tokens: &mut Vec<Token>) -> Result<Node, String> {
    term(tokens) 
}

fn term(tokens: &mut Vec<Token>) -> Result<Node, String> {
    let mut left = factor(tokens)?;

    loop {
        left = match tokens.first() {
            Some(token) => match token {
                Token{token_type: TokenType::Plus, ..} => {
                    tokens.remove(0);
                    Node::BinaryExpr { 
                        op: Operator::Plus, 
                        lhs: Box::new(left), 
                        rhs: Box::new(factor(tokens)?)
                    }
                },
                Token{token_type: TokenType::Minus, ..} => {
                    tokens.remove(0);
                    Node::BinaryExpr { 
                        op: Operator::Minus, 
                        lhs: Box::new(left), 
                        rhs: Box::new(factor(tokens)?)
                    }
                },
                _ => return Ok(left),
            },
            _ => return Ok(left),
        };
    }
}

fn factor(tokens: &mut Vec<Token>) -> Result<Node, String> {
    let mut left = expont(tokens)?;

    loop {
        left = match tokens.first() {
            Some(token) => match token {
                Token{token_type: TokenType::Star, ..} => {
                    tokens.remove(0);
                    Node::BinaryExpr { 
                        op: Operator::Multiply, 
                        lhs: Box::new(left), 
                        rhs: Box::new(expont(tokens)?)
                    }
                },
                Token{token_type: TokenType::Slash, ..} => {
                    tokens.remove(0);
                    Node::BinaryExpr { 
                        op: Operator::Divide, 
                        lhs: Box::new(left), 
                        rhs: Box::new(expont(tokens)?)
                    }
                },
                _ => return Ok(left),
            },
            _ => return Ok(left),
        };
    }
}

fn expont(tokens: &mut Vec<Token>) -> Result<Node, String> {
    let left = unary(tokens)?; 
    match tokens.first() {
        Some(Token { token_type: TokenType::Caret, ..}) => {
            tokens.remove(0);
            Ok(Node::BinaryExpr { 
                op: Operator::Exp, 
                lhs: Box::new(left), 
                rhs: Box::new(expont(tokens)?)
            })
        },
        _ => Ok(left)
    }
}

fn unary(tokens: &mut Vec<Token>) -> Result<Node, String> {
    match tokens.first() {
        Some(token) => match token {
            Token{token_type: TokenType::Minus, ..} => {
                tokens.remove(0);
                Ok(Node::UnaryExpr { 
                    op: Operator::Minus, 
                    child: Box::new(call(tokens)?)
                })
            },
            _ => call(tokens),
        },
        _ => Err("Expected unary expression".to_string()),
    }
}

fn call(tokens: &mut Vec<Token>) -> Result<Node, String> {
    let left = primary(tokens)?;

    match tokens.first() {
        Some(tok) => match tok {
            Token { token_type: TokenType::LeftParen, .. } => {
                tokens.remove(0);
                finish_call(left, tokens)
            },
            _ => {
                Ok(left)
            },
        },
        _ => Ok(left),
    } 
}

fn finish_call(callee: Node, tokens: &mut Vec<Token>) ->  Result<Node, String> {
    let mut args = Vec::new();

    // match callee {
    //     Node::Identifier(_) => (),
    //     _ => return Err(err_no_token("identifier as function callee".to_string()))
    // }

    match tokens.first() {
        Some(tok) => match tok {
            Token { token_type: TokenType::RightParen, .. } => {
                // create the node
                tokens.remove(0);
                return Ok(Node::FuncExpr { name: Box::new(callee), args: args });
            },
            _ => {
                args.push(expression(tokens)?);
                // consume rest of arg list
                loop {
                    match tokens.first() {
                        Some(tok) => match tok {
                            Token { token_type: TokenType::RightParen, .. } => {
                                // create the node
                                tokens.remove(0);
                                return Ok(Node::FuncExpr { name: Box::new(callee), args: args });
                            },
                            Token { token_type: TokenType::Comma, .. } => {
                                tokens.remove(0);
                                args.push(expression(tokens)?);
                                continue;
                            },
                            _ => {
                                return Err(err(tok, "Closing ')' or ',' for function call".to_string()));
                            }
                        },
                        _ => { return Err(err_no_token("Closing ')' for function call".to_string())) }
                    }
                }
            }
        }, 
        // nothing after '('
        _ => {
            return Err(err_no_token("Closing ')' for function call".to_string()));
        }
    }
}

fn primary(tokens: &mut Vec<Token>) -> Result<Node, String> {
    match tokens.first() {
        Some(token) => {
            match token {
                Token { token_type: TokenType::Integer, .. } => {
                    let Ok(i) = token.lexeme.parse::<i32>() else {
                        return Err(err(token, "Int".to_string()))
                    };
                    tokens.remove(0);
                    Ok(Node::Int(i))
                }, 
                Token { token_type: TokenType::Float, .. } => {
                    let Ok(i) = token.lexeme.parse::<f64>() else {
                        return Err(err(token, "Float".to_string()))
                    };
                    tokens.remove(0);
                    Ok(Node::Float(i))
                },
                Token { token_type: TokenType::Identifier, .. } => {
                    Ok(Node::Identifier(tokens.remove(0).lexeme))  
                },
                Token { token_type: TokenType::LeftParen, .. } => {
                    tokens.remove(0);
                    let inner = expression(tokens)?;
                    if let Some(Token { token_type: TokenType::RightParen, .. }) = tokens.first() {
                        tokens.remove(0);
                        Ok(inner)
                    } else if let Some(tok) = tokens.first() {
                        Err(err(tok, "Closing ')'".to_string()))
                    } else {
                        Err(err_no_token("Missing closing ')' at EOF".to_string()))
                    }
                },
                _ => {
                    Err(err(token, "Exprected primary expression".to_string()))
                }
            }
        }, 
        _ => Err(err_no_token("expression".to_string()))
    }
}