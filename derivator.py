from decimal import DivisionByZero
from lexer import Token, TokenType, BinOpType, AstNode
import copy

FUNC_DERS = {
    "sin"   : "cos(x)",
    "cos"   : "-sin(x)",
    "arcsin": "1/sqrt(1-x^2)" 
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
    pass


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

    
global_list = []

def cleanup(node: AstNode) -> AstNode:
    global global_list

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

            return node

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
            # dfs through tree, add nodes contencted via mul to dict
            mul_tokens_list = []
            mul_tokens_list = mul_dfs(node, mul_tokens_list)
            print(mul_tokens_list)


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

            # a/b -> a * b^(-1) - easier for later        
            tmp_exp = AstNode( Token( TokenType.BINOP, BinOpType.EXPONENT))
            # x^(-1)
            tmp_exp.nexts = [childB, AstNode( Token(TokenType.NUMBER, -1))]
            tmp_mul = AstNode( Token( TokenType.BINOP, BinOpType.MULTIPLY))
            tmp_mul.nexts = [childA, tmp_exp]

            return tmp_mul
                
    return node        


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

def mul_list_to_dict(myList: list):
    """
    takes list of operations conected with '*'
    and returns a dict of: { base, list of exponents }
    eg key = 'x', val = [3x, 4, -6, sin(x)] 
    """
    out_list = []
    out_dict = {}
    for node in myList:
        if node.token.type in (TokenType.VAR, TokenType.CONST, TokenType.NUMBER, TokenType.NUM_E, TokenType.FUNC):
            if node.token.value in out_dict:
                # add "1" to list, as its 1 instance of this token value in Mylist
                out_dict[node.token.value].append( AstNode( Token(TokenType.NUMBER, 1) ))
            else:
                # initlialize the list
                out_dict[node.token.value] = [ AstNode( Token(TokenType.NUMBER, 1) ) ] 
        
        # token must be an operation
        elif node.token.type == TokenType.BINOP:
            # nodes we dont want to touch
            if node.token.value in (BinOpType.MINUS, BinOpType.PLUS):
                out_list.append(node)
            # operation type cant be multiply or divide 
            elif node.token.value == BinOpType.EXPONENT:
                pass


