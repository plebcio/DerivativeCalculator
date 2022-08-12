from decimal import DivisionByZero
from lexer import Token, TokenType, BinOpType, AstNode
import copy
import math

func_invers = {
    "sin"   : "arcsin",  
    "cos"   : "arccos",
    "arcsin": "sin",
    "arccos": "cos",
    "tan" : "arctan",
    "arctan": "tan",
    "cot" : "arccot"
}



def derivator(node: AstNode) -> AstNode:
    output_root = AstNode()
    """
    find the type of node - if else statements
    call derive on chid nodes and compose the output and retun as AST
    the AST will later be prosprocesed, like ln(e^x) -> x, x^-5 * x^5 -> x
    """
    if node.token.type == TokenType.NUMBER or node.token.type == TokenType.NUM_E:
        output_root.token = Token( TokenType.NUMBER, 0 )
        # output_root.token = Token( TokenType.NUMBER, node.token.value - 5 )

    # binary operations
    elif node.token.type == TokenType.BINOP:
        if len( node.nexts ) != 2:
            raise Exception( f"BinOp Node: ' {node.token} ' should have 2 child nodes, has {len( node.nexts )}" )
        
        # plus or minus
        if node.token.value == BinOpType.PLUS or node.token.value == BinOpType.MINUS:
            output_root.token = node.token
            output_root.nexts.append( derivator( node.nexts[0] ))
            output_root.nexts.append( derivator( node.nexts[1] ))
            return output_root

        # multiply
        elif node.token.value == BinOpType.MULTIPLY:
            return d_mul(node.nexts[0], node.nexts[1])

        # divide
        elif node.token.value == BinOpType.DIVIDE:
            return d_div(node.nexts[0], node.nexts[1])

        # exponent
        elif node.token.value == BinOpType.EXPONENT:
            return d_exp(node.nexts[0], node.nexts[1])
        
    # func
    elif node.token.type == TokenType.FUNC:
        return d_func(node)
    

    # var x
    elif node.token.type == TokenType.VAR:
        #return AstNode( Token( TokenType.VAR, 'x\'' ))
        return AstNode( Token( TokenType.NUMBER, 1 ))

    return output_root


def d_func(node: AstNode) -> AstNode:
    # check for inverse functions and simplify
    if node.token.value in func_invers:
        if func_invers[node.token.value] == node.nexts[0].token.value:
            print("pppp")
            return derivator(node.nexts[0].nexts[0])

    # chain rule
    # f(g(x)) -> f'(g) * g'
    tmp_mul = AstNode( Token( TokenType.BINOP, BinOpType.MULTIPLY ) )
    # f'(g)
    tmp_mul.nexts.append( d_func_helper(node.token.value, node.nexts[0]) )
    # g'
    tmp_mul.nexts.append( derivator(node.nexts[0]) )
    
    return tmp_mul


def d_func_helper(f_name, child_node: AstNode)-> AstNode:
    # returns the derivative of fucntion f_name with arg child_node
    # return f'(g) where f_name is f, and child node is g

    # exprssion is a const -> derivative is zero
    if child_node.token.type == TokenType.NUMBER:
        return AstNode(Token(TokenType.NUMBER, 0 ))

    if f_name == "sin":
        # cos(x)
        return AstNode(Token(TokenType.FUNC, 'cos'), [child_node])
    
    elif f_name == "cos":
        # -1*sin(x)
        return AstNode(Token(TokenType.BINOP, BinOpType.MULTIPLY), [
            AstNode(Token(TokenType.FUNC, 'sin'), [child_node]),
            AstNode(Token( TokenType.NUMBER, -1 ))  
            ])

    elif f_name == "ln":
        # 1/x -> x^-1
        return AstNode(Token(TokenType.BINOP, BinOpType.EXPONENT), [
            child_node, AstNode(Token( TokenType.NUMBER, -1 ))])
    
    elif f_name == "arcsin":
        # 1/(1-x^2)^(1/2)
        return AstNode(Token(TokenType.BINOP, BinOpType.EXPONENT), [
            AstNode(Token( TokenType.BINOP, BinOpType.MINUS ), [
                AstNode(Token( TokenType.NUMBER, -1 )), AstNode(Token(TokenType.BINOP, BinOpType.EXPONENT), [
                    child_node, AstNode(Token( TokenType.NUMBER, 2 ))
                    ])
                ]),
            AstNode(Token( TokenType.NUMBER, -0.5 )),
            ])

    elif f_name == "tan":
        # cheat - return (sin/cos)'
        return derivator(AstNode(Token(TokenType.BINOP, BinOpType.DIVIDE), [
            AstNode(Token(TokenType.FUNC, 'sin'), [child_node]),
            AstNode(Token(TokenType.FUNC, 'cos'), [child_node]),
        ]))

    elif f_name == "cot":
        # cheat - retrun ((tan)^-1)'
        return derivator(AstNode(Token(TokenType.BINOP, BinOpType.EXPONENT), [
            AstNode(Token(TokenType.FUNC, 'tan'), [child_node]),
            AstNode(Token(TokenType.NUMBER, -1)),
        ]))


# derivative of multiplication
def d_mul(a: AstNode, b: AstNode) -> AstNode:
    # a*b -> a*b' + a'*b
    out = AstNode( Token( TokenType.BINOP, BinOpType.PLUS ) )
    childA = AstNode()
    childB = AstNode()
    childA.token = Token( TokenType.BINOP, BinOpType.MULTIPLY )
    childB.token = Token( TokenType.BINOP, BinOpType.MULTIPLY )
    childA.nexts.append( a ) # a
    childA.nexts.append( derivator( b )) # b'
    childB.nexts.append( derivator( a )) # a'
    childB.nexts.append( b ) # b
    out.nexts.append(childA)
    out.nexts.append(childB)

    return out

def d_div(a: AstNode, b: AstNode) -> AstNode:
    out = AstNode()
    
    # a/b -> (a' * b - b' * a)/ (b^2)
    out.token = Token( TokenType.BINOP, BinOpType.DIVIDE )
    # create a' * b - b' * a
    tmp_mul1 = AstNode()
    tmp_mul2 = AstNode()
    tmp_min  = AstNode()
    tmp_exp  = AstNode()
    # a' * b
    tmp_mul1.token = Token( TokenType.BINOP, BinOpType.MULTIPLY )
    tmp_mul1.nexts.append( derivator(a) ) # a'
    tmp_mul1.nexts.append( b ) # b
    # b' * a
    tmp_mul2.token = Token( TokenType.BINOP, BinOpType.MULTIPLY )
    tmp_mul2.nexts.append( derivator(b) ) # b'
    tmp_mul2.nexts.append( a ) # a
    # (a' * b - b' * a)
    tmp_min.token = Token( TokenType.BINOP, BinOpType.MINUS )
    tmp_min.nexts.append(tmp_mul1)
    tmp_min.nexts.append(tmp_mul2)
    # (b^2)
    tmp_exp.token = Token( TokenType.BINOP, BinOpType.EXPONENT )
    tmp_exp.nexts.append( b )
    tmp_exp.nexts.append( AstNode( Token( TokenType.NUMBER, 2 )))

    out.nexts.append(tmp_min)
    out.nexts.append(tmp_exp)

    return out


def d_exp(f: AstNode, g: AstNode) -> AstNode:
    # f^g = f^g * ( f' * (g/f) + g' * ln(f)  )
    tmp_mul1 = AstNode( Token(TokenType.BINOP, BinOpType.MULTIPLY ))
    tmp_mul2 = AstNode( Token(TokenType.BINOP, BinOpType.MULTIPLY ))
    tmp_mul3 = AstNode( Token(TokenType.BINOP, BinOpType.MULTIPLY ))
    tmp_sum  = AstNode( Token(TokenType.BINOP, BinOpType.PLUS ))
    tmp_div  = AstNode( Token(TokenType.BINOP, BinOpType.DIVIDE ))
    tmp_ln   = AstNode( Token(TokenType.FUNC, "ln" ))
    tmp_exp  = AstNode( Token(TokenType.BINOP, BinOpType.EXPONENT ))

    tmp_exp.nexts = [f,g]
    tmp_div.nexts = [g,f]
    tmp_ln.nexts = [f]
    # f' * (g/f)
    tmp_mul2.nexts = [derivator(f), tmp_div]
    # g' * ln(f)
    tmp_mul3.nexts = [ derivator( g ), tmp_ln ]
    #( f' * (f/g) + g' * ln(f)  )
    tmp_sum.nexts = [tmp_mul2, tmp_mul3]
    tmp_mul1.nexts = [tmp_exp, tmp_sum]
    
    # TODO maybe cleanup already
    return tmp_mul1


def cleanup(node: AstNode) -> AstNode:

    if len(node.nexts) == 0:
        return node

    # clean up subtrees
    tmp_l = []
    for child in node.nexts:
        tmp_l.append(cleanup(child))
    node.nexts = tmp_l


    if node.token.type == TokenType.BINOP:
        childA, childB = node.nexts
        if node.token.value == BinOpType.PLUS:
            # add two numbers
            if childA.token.type == TokenType.NUMBER and childB.token.type == TokenType.NUMBER:
                return AstNode( Token( TokenType.NUMBER, childA.token.value + childB.token.value) ) 
            # childA is zero
            if childA.token.type == TokenType.NUMBER and childA.token.value == 0:
                return childB
            # childB is zero
            if childB.token.type == TokenType.NUMBER and childB.token.value == 0:
                return childA

            # trig identity sin2 + cos2 = 1
            if childA.token.value == childB.token.value == BinOpType.EXPONENT:
                if childA.nexts[1].token.value == childB.nexts[1].token.value == 2:
                    if {childA.nexts[0].token.value, childB.nexts[0].token.value} == {"sin", "cos"}:
                        return AstNode(Token(TokenType.NUMBER, 1))

            # weird func stuff
            if childA.token.type == TokenType.FUNC and childB.token.type == TokenType.FUNC:
                # if both childs have the same arg
                if childA.nexts[0] == childB.nexts[0]:
                    pass 

            return node
        
        if node.token.value == BinOpType.MINUS:
            # sub two numbers
            if childA.token.type == TokenType.NUMBER and childB.token.type == TokenType.NUMBER:
                return AstNode( Token( TokenType.NUMBER, childA.token.value - childB.token.value) ) 
            # childB is zero
            if childB.token.type == TokenType.NUMBER and childB.token.value == 0:
                return childA
            # childA is zero: 0 -(expres) -> -1*(expres)
            if childA.token.type == TokenType.NUMBER and childA.token.value == 0:
                return childB

            # a-b -> a + (-1)*b
            return cleanup( AstNode( Token( TokenType.BINOP, BinOpType.PLUS), [
                childA, AstNode( Token( TokenType.BINOP, BinOpType.MULTIPLY), [
                    AstNode( Token(TokenType.NUMBER, -1)), childB
                ])]
            ))
            
        if node.token.value == BinOpType.MULTIPLY:
            # mul two numbers
            if childA.token.type == TokenType.NUMBER and childB.token.type == TokenType.NUMBER:
                return AstNode( Token( TokenType.NUMBER, childA.token.value * childB.token.value) ) 
            # childA is zero
            if childA.token.type == TokenType.NUMBER and childA.token.value == 0:
                return AstNode( Token( TokenType.NUMBER, 0 ))
            # childB is zero
            if childB.token.type == TokenType.NUMBER and childB.token.value == 0:
                return AstNode( Token( TokenType.NUMBER, 0 ))

            # childA is 1
            if childA.token.type == TokenType.NUMBER and childA.token.value == 1:
                return childB

            # childB is 1
            if childB.token.type == TokenType.NUMBER and childB.token.value == 1:
                return childA

            # simplifying mul trains into exponets eg: x*5*x*x^7 -> 5*x^9
            # ----- section for simplifiing these mul train --- 
            # dfs through tree, add nodes contencted via mul to dict
            def mul_dfs(node: AstNode, myList: list): 
                if node.nexts[0].token.value == BinOpType.MULTIPLY:
                    mul_dfs(node.nexts[0], myList)
                else:
                    myList.append(node.nexts[0])

                if node.nexts[1].token.value == BinOpType.MULTIPLY:
                    mul_dfs(node.nexts[1], myList)
                else:
                    myList.append(node.nexts[1])

                return myList

            print("---"*8)
            print("Cleainig node", node)

            mul_tokens_list = []
            list1 = mul_dfs(node, mul_tokens_list)
            print(list1)
            tmp_dict, tmp_list = mul_list_to_dict(list1)
            print(tmp_dict, tmp_list)
            node = reconstruct_tree( tmp_dict, tmp_list )
            print(node)
            print("---"*8)
            # TODO ineficitnte but whatever
            # clean up subtrees
            # tmp_l = []
            # for child in node.nexts:
            #     tmp_l.append(cleanup(child))
            # node.nexts = tmp_l
            # print("---"*8)

            return node

        if node.token.value == BinOpType.DIVIDE:
            # div two numbers
            if childA.token.type == TokenType.NUMBER and childB.token.type == TokenType.NUMBER:
                return AstNode( Token( TokenType.NUMBER, childA.token.value / childB.token.value) ) 
            # childA is zero
            if childA.token.type == TokenType.NUMBER and childA.token.value == 0:
                return AstNode( Token( TokenType.NUMBER, 0 ))
            # childB is zero
            if childB.token.type == TokenType.NUMBER and childB.token.value == 0:
                raise DivisionByZero
            
            # TODO check if this really is easier for later
            # a/b -> a * b^(-1) - easier for later        
            print("division trick:")
            print(node)
            tmp_exp = AstNode( Token( TokenType.BINOP, BinOpType.EXPONENT))
            # x^(-1)
            tmp_exp.nexts = [childB, AstNode( Token(TokenType.NUMBER, -1))]
            tmp_mul = AstNode( Token( TokenType.BINOP, BinOpType.MULTIPLY))
            tmp_mul.nexts = [childA, tmp_exp]
            print(tmp_mul)
            # call cleanup on itself after change for div to mul
            tmp_mul = cleanup(tmp_mul)
            print(tmp_mul)
            print("***********"*5)
            return tmp_mul

        if node.token.value == BinOpType.EXPONENT:
            # two numbers
            if childA.token.type == TokenType.NUMBER and childB.token.type == TokenType.NUMBER:
                return AstNode( Token( TokenType.NUMBER, childA.token.value**childB.token.value) ) 
            # childA is zero
            if childA.token.type == TokenType.NUMBER and childA.token.value == 0:
                return AstNode( Token( TokenType.NUMBER, 0 ))
            # childB is zero
            if childB.token.type == TokenType.NUMBER and childB.token.value == 0:
                return AstNode( Token( TokenType.NUMBER, 1 ))
            # childB is one
            if childB.token.type == TokenType.NUMBER and childB.token.value == 1:
                return childA

            # (a^b)^c -> a^(b*c)
            # rember to cleanup currnode at the end - maybe inefficient but whatever
            if childA.token.type == TokenType.BINOP and childA.token.value == BinOpType.EXPONENT:
                # b*c
                tmp_mul = AstNode( Token( TokenType.BINOP, BinOpType.MULTIPLY), [
                    childA.nexts[1], childB  ])
                # a^(b*c)
                node.nexts = [childA.nexts[0], tmp_mul]
                # cleanup new root node
                return cleanup(node)

    elif node.token.type == TokenType.FUNC:
        pass
                
    return node        


def func_cleanup(node: AstNode):
    pass


def mul_list_to_dict(myList: list):
    """
    takes list of operations conected with '*'
    and returns a dict of: { base, list of exponents }
    eg key = Astnode, like (Token = VAR x, nexts=[]) , val = [3x, 4, -6, sin(x)] !!! changed 
    Functions cannot be keys - keys cannot have next lists TODO handle fucntions
    """
    # change outdict to list of tuples so i can have nodes as keys
    # [(key, val)] - slower but now (x+1) can be a key
    out_list = []
    out_dict = []
    out_num = 1
    for node in myList:
        if node.token.type == TokenType.NUMBER:
            out_num *= node.token.value

        elif node.token.type in (TokenType.VAR, TokenType.CONST, TokenType.NUM_E):
            # find index of the node that should be added to the "dict"
            node_index = next((i for i, x in enumerate(out_dict) if x[0] == node), None)
            if node_index != None:
                # add "1" to list, as its 1 instance of this token value in Mylist
                out_dict[node_index][1].append( AstNode( Token(TokenType.NUMBER, 1) ))
            else:
                # initlialize the list
                out_dict.append( (node,[AstNode( Token(TokenType.NUMBER, 1))] )) 
        
        # if token is exponent
        elif node.token.value == BinOpType.EXPONENT:
            # we will only simplify one node deep
            # if left node is not in 
            # (TokenType.VAR, TokenType.CONST, TokenType.NUMBER, TokenType.NUM_E)  
            # then it we be left as is
            if node.nexts[0].token.type in \
                    (TokenType.VAR, TokenType.CONST, TokenType.NUMBER, TokenType.NUM_E):
                    node_child_index = next((i for i, x in enumerate(out_dict) if x[0] == node.nexts[0]), None)
                # add the exponent to list
                    if node_child_index != None:
                        out_dict[node_child_index][1].append( node.nexts[1] )
                    else:
                    # initlialize the tuple (key, list) 
                        out_dict.append( (node, [ node.nexts[1] ]) )

            # if exponent to complex, add it to out_list
            else:
                out_list.append(node)
    
        # handle the rest of the input
        else:       
            # handles complex exponents, +, - and maybe other things - functions ??
            out_list.append(node)
    
    # group all the numbers into a single node
    if out_num != 1:
        out_list.insert(0, AstNode( Token(TokenType.NUMBER, out_num) ) )
    
    return out_dict, out_list


def reconstruct_tree(mul_dict: dict, mul_list: 'list[AstNode]'):
    # loop over nodes in dict and list
    # contruct exponents and link them with mul nodes

    # construct PLUS nodes from the lists in mul_dict
    # and create a list of exponents
    exponent_list = [] 
    for key, val in mul_dict:
        tmp_exp = AstNode( Token(TokenType.BINOP, BinOpType.EXPONENT ))
        tmp_exp.nexts.append(key)
        # cleanup the exponent before adding to the node
        tmp_exp.nexts.append(cleanup(list_to_operator_ast(val, BinOpType.PLUS)))
        exponent_list.append(tmp_exp)
    
    # connect the exponent list and the mul_list given as arg to the function
    # into one mul tree
    # and retrun it
    return list_to_operator_ast(exponent_list + mul_list, BinOpType.MULTIPLY)
    


def list_to_operator_ast(main_list:list, opetype:BinOpType):
    if len(main_list) == 0:

        raise Exception("how ?")

     # only one elem, so no point in creating tree
    if len(main_list) == 1:
        return main_list[0]


    out_list = []
    for node in main_list:
        tmp_plus1 = AstNode( Token(TokenType.BINOP, opetype ))
        tmp_plus1.nexts.append(node)
        out_list.append(tmp_plus1)

    
    # does nothing for list of len <= 2
    for i, node in enumerate(out_list[0:-2:]):
        node.nexts.append(out_list[i + 1])
       
    # last element has no nexts[1] - so its a redundant plus node 
    # so second to last element, a plus node, gets the redundant plus node's nexts[0] arg
    out_list[-2].nexts.append(out_list[-1].nexts[0])
    
    return out_list[0] 
