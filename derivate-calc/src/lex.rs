use std::{iter::Peekable, str::Chars};

use super::grammar;

use grammar::{Token, TokenType};

// for example, with the following expr:
// 1 + 2 - sin(3) * 4

// the lexer will produce the following tokens: 
// Number(1), Plus, Number(2), Minus, Identifier(sin), LeftParen, Number(3), RightParen, Star, Number(4)

struct LexerState {
    line: i32,
    current_lexme: String,
    tokens: Vec<Token>, 
}

impl LexerState {
    pub fn new() -> LexerState {
        LexerState{
            line: 0,
            current_lexme: String::new(),
            tokens: Vec::new(),
        }
    }

    // allway flush the current lexme
    fn add_token(&mut self, token: Token){
        self.close_lexme();
        self.tokens.push(Token{line: self.line, ..token});
    }

    fn close_lexme(&mut self){
        if self.current_lexme.len() > 0 {
            self.tokens.push(Token{token_type: TokenType::Identifier, lexeme: self.current_lexme.clone(), line: self.line});
            self.current_lexme.clear();
        }
    }

    fn add_char(&mut self, c: char){
        self.current_lexme.push(c);
    }

    fn add_str(&mut self, s: &str){
        self.current_lexme.push_str(s);
    }

    fn line(&self) -> i32 {
        self.line
    }
}

pub fn lexer(input: &String) -> Result<Vec<Token>, String>{
    lexer_impl(input, LexerState::new())
}

fn lexer_impl(input: &String, mut lexer: LexerState) -> Result<Vec<Token>, String> {

    let lines = input.split("\n");

    for line in lines {
        let mut chars = line.chars().peekable();
        lexer.line += 1;
        loop {
            match chars.peek() {
                Some('(') => {
                    lexer.add_token(Token::new(TokenType::LeftParen, "(".to_string()));
                    chars.next();
                },
                Some(')') => {
                    lexer.add_token(Token::new(TokenType::RightParen, ")".to_string()));
                    chars.next();
                },
                Some('+') => {
                    lexer.add_token(Token::new(TokenType::Plus, "+".to_string()));
                    chars.next();
                },
                Some('-') => {
                    lexer.add_token(Token::new(TokenType::Minus, "-".to_string()));
                    chars.next();
                },
                Some('*') => {
                    lexer.add_token(Token::new(TokenType::Star, "*".to_string()));
                    chars.next();
                },
                Some('/') => {
                    lexer.add_token(Token::new(TokenType::Slash, "/".to_string()));
                    chars.next();
                },
                Some('^') => {
                    lexer.add_token(Token::new(TokenType::Caret, "^".to_string()));
                    chars.next();
                },
                Some(',') => {
                    lexer.add_token(Token::new(TokenType::Comma, ",".to_string()));
                    chars.next();
                },
                Some(' ') | Some('\t') | Some('\n')  => {
                    // end current lexeme
                    lexer.close_lexme();
                    chars.next();
                },
                Some(c) if c.is_digit(10) => {
                    print!("lexme at num: {}\n", lexer.current_lexme);
                    let num = number(&mut chars);
                    print!("num: {:?}\n", num);
                    print!("num: {}\n", num.lexeme);
                    lexer.add_token(num);
                },
                Some(c) if c.is_ascii_alphabetic() => {
                    println!("Ident start {}", c);
                    let ident = identifier(&mut chars);
                    lexer.add_token(ident);
                },
                Some(token) => {
                    return Err(format!("Error on line {}: Unknow token '{}'", lexer.line(), token));
                },
                None => {
                    // end current lexeme
                    lexer.close_lexme();
                    break;
                }
            }
        }
    }

    Ok(lexer.tokens)
}


// at this point one digit has been read
fn number(chars: &mut Peekable<Chars<'_>> ) -> Token {
    let mut matched = String::new();
    loop {
        match chars.peek() {
            Some(c) if c.is_ascii_digit() => {
                matched.push(*c); chars.next();
            },
            Some(c) if *c == '.' => {
                matched.push(*c); 
                chars.next();
                break;
            },
            _ => {
                // it's an int
                return Token{
                        token_type: TokenType::Integer, 
                        lexeme: matched, 
                        line: 0
                    };
            }
        }
    }

    // it's a float
    while let Some(c) = chars.peek(){
        if c.is_ascii_digit() {
            matched.push(*c);
            chars.next();
        } else {
            break;
        }
    }

    print!("matched: {}\n", matched);

    Token{
            token_type: TokenType::Float, 
            lexeme: matched, 
            line: 0
    }
}

fn identifier(chars: &mut Peekable<Chars<'_>> ) -> Token {
    let mut matched = String::new();
    loop {
        match chars.peek() {
            Some(c) if c.is_ascii_alphabetic() => {
                matched.push(*c); chars.next();
            },
            _ => {
                return Token{
                        token_type: TokenType::Identifier, 
                        lexeme: matched, 
                        line: 0
                    };
            }
        }
    }
}
