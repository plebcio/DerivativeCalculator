#[derive(PartialEq, Debug, Clone, Copy)]
pub enum Operator {
    Plus,
    Minus,
    Divide,
    Multiply,
    Exp
}

pub enum Node {
    Int(i32),
    Float(f64),
    Identifier(String),
    UnaryExpr {
        op: Operator,
        child: Box<Node>,
    },
    BinaryExpr {
        op: Operator,
        lhs: Box<Node>,
        rhs: Box<Node>,
    },
    FuncExpr {
        name: Box<Node>, // prefarably Identifier
        args: Vec<Node>
    },
    CombinedMult {
        terms: Vec<Node>
    }
}

impl Node {
    // write print function here
    pub fn print(&self) {
        match self {
            Node::Int(value) => print!("{}", value),
            Node::Float(value) => print!("{}", value),
            Node::Identifier(name) => print!("{}", name),
            Node::UnaryExpr { op, child } => {
                print!("(");
                match op {
                    Operator::Plus => print!("+"),
                    Operator::Minus => print!("-"),
                    Operator::Divide => print!("/"),
                    Operator::Multiply => print!("*"),
                    Operator::Exp => print!("^"),
                }
                child.print();
                print!(")");
            }
            Node::BinaryExpr { op, lhs, rhs } => {
                print!("(");
                lhs.print();
                match op {
                    Operator::Plus => print!(" + "),
                    Operator::Minus => print!(" - "),
                    Operator::Divide => print!(" / "),
                    Operator::Multiply => print!(" * "),
                    Operator::Exp => print!(" ^ "),
                }
                rhs.print();
                print!(")");
            }
            Node::FuncExpr { name, args } => {
                name.print();
                print!("(");
                for (i, arg) in args.iter().enumerate() {
                    if i > 0 {
                        print!(", ");
                    }
                    arg.print();
                }
                print!(")");
            },
            Node::CombinedMult { terms } => {
                print!("(");
                for (i, arg) in terms.iter().enumerate() {
                    if i > 0 {
                        print!(", ");
                    }
                    arg.print();
                } 
                print!(")");
            }
        }
    } 
}

impl Clone for Node {
    fn clone(&self) -> Node {
        match self {
            Node::Int(value) => Node::Int(*value),
            Node::Float(value) => Node::Float(*value),
            Node::Identifier(name) => Node::Identifier(name.clone()),
            Node::UnaryExpr { op, child } => Node::UnaryExpr {
                op: *op,
                child: child.clone(),
            },
            Node::BinaryExpr { op, lhs, rhs } => Node::BinaryExpr {
                op: *op,
                lhs: lhs.clone(),
                rhs: rhs.clone(),
            },
            Node::FuncExpr { name, args } => Node::FuncExpr {
                name: name.clone(),
                args: args.clone(),
            },
            Node::CombinedMult { terms } => Node::CombinedMult { terms: terms.clone() }
        }
    }
    
}

#[derive(Debug, Clone, Copy)]
pub enum TokenType {
    // Single-character tokens
    LeftParen, RightParen, Comma,

    Integer, Float,
    Plus, Minus, Star, Slash, Caret,
    Identifier
}

#[derive(Debug, Clone)]
pub struct Token {
        pub token_type: TokenType,
        pub lexeme: String,
        pub line: i32,
}

impl Token {
    pub fn new(token_type: TokenType, lexeme: String) -> Token {
        Token{token_type, lexeme, line: 0}
    }
    
}