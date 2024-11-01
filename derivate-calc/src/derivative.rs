use crate::grammar::*;
use core::f64;
use std::collections::HashMap;

pub type DerivativeLookup = HashMap<String, Box<dyn Fn(&Vec<Node>) -> Result<Node, String>>> ;

pub fn check_call_types(tree: &Node, known_funcs: &HashMap<String, usize>) -> Result<(), String> {
    match *tree {
        Node::FuncExpr { ref name, ref args } => {
            let func_name = match **name {
                Node::Identifier(ref name) => name,
                Node::Float(_) | Node::Int(_) => {
                    // 3(args) is a valid expression only if args just one argument
                    if args.len() == 1 {
                        return check_call_types(&args[0], known_funcs)
                    } else {
                        return Err("Multiargument function name must be an identifier".to_string())
                    }
                }
                _ => return Err("Function name must be an identifier".to_string())
            };
            let arg_num = match known_funcs.get(func_name){
                None => return Err(format!("Unknown function {}", func_name)),
                Some(num) => num,
            };

            if *arg_num != args.len(){
                return Err(format!("Function {} expects {} arguments, got {}", func_name, arg_num, args.len()));
            } 

            for arg in args.iter(){
               let res = check_call_types(arg, known_funcs);
                if res.is_err(){
                    return res;
                }
            }
            return Ok(())
        },
        Node::BinaryExpr { ref lhs, ref rhs, .. } => {
            check_call_types(lhs.as_ref(), known_funcs).and(check_call_types(rhs.as_ref(), known_funcs))
        },
        Node::UnaryExpr { ref child, .. } => {
            check_call_types(child.as_ref(), known_funcs)
        },
        _ => Ok(())
    }
}

fn minus_one(n: Node) -> Box<Node> {
   Box::new(Node::BinaryExpr { op: Operator::Minus, lhs: Box::new(n), rhs: Box::new(Node::Int(1))})
}

pub fn derivative(tree: &Node, know_derivatices: &DerivativeLookup) -> Result<Node, String> {
    match tree {
        Node::Float(_) | Node::Int(_) => Ok(Node::Int(0)),
        Node::Identifier(ref name) => {
            match know_derivatices.get(name) {
                Some(_) => Err("Can't take derivative of function".to_string()),
                None => Ok(Node::Int(1))
            }
        },
        Node::BinaryExpr { op, lhs, rhs } => {
            match op {
                Operator::Plus => Ok(Node::BinaryExpr {
                    op: Operator::Plus,
                    lhs: Box::new(derivative(lhs.as_ref(), know_derivatices)?),
                    rhs: Box::new(derivative(rhs.as_ref(), know_derivatices)?)
                }),
                Operator::Multiply => Ok(Node::BinaryExpr { 
                    op: Operator::Plus, 
                    lhs: Box::new(Node::BinaryExpr { 
                        op: Operator::Multiply, 
                        lhs: lhs.clone(), 
                        rhs: Box::new(derivative(rhs.as_ref(), know_derivatices)?) 
                    }), 
                    rhs: Box::new(Node::BinaryExpr { 
                        op: Operator::Plus, 
                        lhs: Box::new(derivative(lhs.as_ref(), know_derivatices)?), 
                        rhs: rhs.clone()
                    }) 
                }),
                Operator::Minus => Ok(Node::BinaryExpr {
                    op: Operator::Minus,
                    lhs: Box::new(derivative(lhs.as_ref(), know_derivatices)?),
                    rhs: Box::new(derivative(rhs.as_ref(), know_derivatices)?)
                }),
                Operator::Exp =>  {
                    if let i @ Node::Int(_) | i @ Node::Float(_) = lhs.as_ref() {
                        // we have a ^ some_exp
                        Ok(Node::BinaryExpr { 
                            op: Operator::Multiply, 
                            lhs: Box::new(Node::BinaryExpr { 
                                op: Operator::Exp, 
                                lhs: Box::new(i.clone()), 
                                rhs: rhs.clone()
                            }), 
                            rhs: Box::new(Node::FuncExpr { 
                                name: Box::new(Node::Identifier("ln".to_string())), 
                                args: Vec::from([i.clone()])
                            })
                        })
                    } else if let i @ Node::Int(_) | i @ Node::Float(_) = rhs.as_ref() {
                        // we have some_exp ^ i
                        // [u(x)^n]' = n * u(x)^(n-1) * [u(x)]'
                        Ok(Node::BinaryExpr { 
                            op: Operator::Multiply, 
                            lhs: Box::new(i.clone()), 
                            rhs: Box::new(Node::BinaryExpr { 
                                op: Operator::Multiply, 
                                rhs: Box::new(Node::BinaryExpr { 
                                    op: Operator::Exp, 
                                    lhs: lhs.clone(), 
                                    rhs: minus_one(i.clone()) 
                                }),
                                lhs: Box::new(derivative(lhs, know_derivatices)?)
                            })
                        })
                    } else {
                        Err("Too hard".to_string())
                    }
                }
                _ => panic!("Derivative not implemented for this operator"),
            }
        }
        Node::FuncExpr { name, args } => {
            let derivs : Vec<Node> = args
                .iter()
                .map(|arg| derivative(arg, know_derivatices) )
                .collect::<Result<_, _>>()?;

            
            match name.as_ref() {
                Node::Float(_) | Node::Int(_) => {
                    // 3(args) is a valid expression only if args just one argument
                    if args.len() == 1 {
                        Ok(Node::BinaryExpr { 
                            op: Operator::Multiply, 
                            lhs: name.clone(), 
                            rhs: Box::new(derivs[0].clone()) 
                        })
                    } else {
                        Err("Multi argument function name must be an identifier".to_string())
                    }
                },
                Node::Identifier(name) => {
                    // f(g(x)) = f'(g(x))*g'(x)
                    match know_derivatices.get(name) {
                        Some(func) => {
                            // this is f'(g(x))
                            let left = func(args)?;
                            Ok(Node::BinaryExpr { 
                                op: Operator::Multiply,
                                lhs: Box::new(left.clone()), 
                                rhs: Box::new(derivs[0].clone()) 
                            })
                        },
                        None => Err(format!("Unknown function {}", name))
                    } 
                },
                _ => return Err("Function name must be an identifier".to_string())
            }
        },
        Node::UnaryExpr { op: _op, child } => {
            Ok(Node::BinaryExpr { 
                op: Operator::Multiply, 
                lhs: Box::new(Node::Int(-1)), 
                rhs: Box::new(derivative(child, know_derivatices)?) 
            })
        },
        _ => Err(format!("Not implemented"))
    }
}

pub fn simplify(mut tree: Node) ->  Node {
    loop {
        let (succ, new_tree) = simplify_impl(tree);
        if !succ {
            return new_tree;
        }
        tree = new_tree;
    }
}

fn simplify_impl(tree: Node) ->  (bool, Node) {
    match tree {
        // first sipmlify the children
        Node::BinaryExpr { op, lhs, rhs } => {
            let (succ1, lhs) = simplify_impl(*lhs);
            let (succ2, rhs) = simplify_impl(*rhs);
            let succ = succ1 || succ2;
            match (op, lhs, rhs) {
                // 0 + x = x
                (Operator::Plus, Node::Int(0), x) => (true, x),
                // x + 0 = x
                (Operator::Plus, x, Node::Int(0)) => (true, x),
                // 0 * x = 0
                (Operator::Plus, Node::Int(a), Node::Int(b)) => (true, Node::Int(a+b)),
                (Operator::Plus, Node::Float(a), Node::Float(b)) => (true, Node::Float(a+b)),
                
                (Operator::Multiply, Node::Int(0), _) => (true, Node::Int(0)),
                // x * 0 = 0
                (Operator::Multiply, _, Node::Int(0)) => (true, Node::Int(0)),
                // 1 * x = x
                (Operator::Multiply, Node::Int(1), x) => (true, x),
                // x * 1 = x
                (Operator::Multiply, x, Node::Int(1)) => (true, x),
                // x - 0 = x
                (Operator::Multiply, Node::Int(a), Node::Int(b)) => (true, Node::Int(a*b)),
                (Operator::Multiply, Node::Float(a), Node::Float(b)) => (true, Node::Float(a*b)),

                (Operator::Minus, x, Node::Int(0)) => (true, x),
                (Operator::Minus, Node::Int(a), Node::Int(b)) => (true, Node::Int(a-b)),
                (Operator::Minus, Node::Float(a), Node::Float(b)) => (true, Node::Float(a-b)),
                
                // x / 1 = x
                (Operator::Divide, x, Node::Int(1)) => (true, x),
                (Operator::Divide, Node::Int(a), Node::Int(b)) => (true, Node::Float(a as f64 / b as f64)),
                (Operator::Divide, Node::Float(a), Node::Float(b)) => (true, Node::Float(a/b)),
                // x ^ 0 = 1
                (Operator::Exp, x, Node::Int(0)) => (true, Node::Int(1)),
                // x ^ 1 = x
                (Operator::Exp, x, Node::Int(1)) => (true, x),
                (Operator::Exp, Node::Int(a), Node::Int(b)) if b > 0 => (true, Node::Int(a.pow(b.try_into().unwrap()))),
                (Operator::Exp, Node::Float(a), Node::Float(b)) => (true, Node::Float(a.powf(b))),
                

                (op, lhs, rhs) => (succ, Node::BinaryExpr { op, lhs: Box::new(lhs), rhs: Box::new(rhs) })
            }
        }, 
        _ => (false, tree)
    }
}

fn d_ln(d_args: &Vec<Node>) -> Result<Node, String> {
    Ok(Node::BinaryExpr { 
        op: Operator::Divide, 
        lhs: Box::new(Node::Int(1)), 
        rhs: Box::new(d_args[0].clone()) 
    })
}

pub fn get_know_derivatives() -> DerivativeLookup {
    let mut map: DerivativeLookup = HashMap::new();
    
    map.insert("ln".to_string(), Box::new(|args: &Vec<Node>| {
        Ok(Node::BinaryExpr { 
            op: Operator::Divide, 
            lhs: Box::new(Node::Int(1)), 
            rhs: Box::new(args[0].clone()) 
        })
    }));

    map
}