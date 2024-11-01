mod lex;
mod grammar;
mod parser;
mod derivative;

use std::{env, process::exit};

use derivative::get_know_derivatives;


#[cfg(test)]
mod test {
    use super::*;

    // #[test]
    // fn try_eval_test(){
    //     let n = Node::BinaryExpr {
    //         op: Operator::Plus,
    //         lhs: Box::new(Node::Int(1)),
    //         rhs: Box::new(Node::Int(2))
    //     };
    //     assert!(try_eval(n).unwrap() == 3.0);
    // }
}

fn main() {
    
    let known_funcs = std::collections::HashMap::from([
        ("ln".to_string(), 1)
    ]);


    let args: Vec<_> = env::args().collect();
    if args.len() < 1 {
        println!("Please provide an expression to parse");
    }
    let input = &args[1];
    let tokens = match lex::lexer(&input) {
        Ok(ok) => ok,
        Err(err) => {
            println!("Tokenization failed");
            println!("{}", err);
            exit(1);
        }
    };


    println!("parsing");
    let node = parser::parse(tokens).expect("failed to parse tokens");
    node.print();

    let known_funcs = std::collections::HashMap::from([
        ("ln".to_string(), 1),
        ("cos".to_string(), 1)
    ]);

    println!("");

    let type_check =  derivative::check_call_types(&node, &known_funcs);
    match type_check {
        Ok(_) => println!("Type check passed"),
        Err(err) => {
            println!("Type check failed");
            println!("{}", err);
            exit(1);
        }
    }

    println!("Derivative");

    let deriv = derivative::derivative(&node, &derivative::get_know_derivatives());

    match deriv {
        Ok(node) => {
            node.print();
            println!("");
            derivative::simplify(node).print();
            println!("");
        },
        Err(err) => {
            println!("Derivative failed");
            println!("{}", err);
            exit(1);
        }
    }
}

