"""
codes: 0: num, 1: bianryOp1 (+, -), 2: bianryOp2 (*, /), 3: bianryOp3 ( ^ ), 4: parems '()',  5: uniaryOp ( sin, exp, log, ln  )
"""
VAR_NAME = ["x", "y", "z"]

from cgi import print_arguments
from dataclasses import dataclass
from distutils.util import change_root
from enum import Enum
import copy

WHITESPACE = " \t\n"
DIGITS = "0123456789"

FUNC_NAMES = ['sin', 'cos', 'exp', 'arcsin', "sqrt", "ln", "tan", "cot"]

class TokenType(Enum):

    NUMBER   = 0
    BINOP    = 1
    LPEREN   = 2
    RPAREN   = 3
    FUNC     = 4
    CONST    = 5
    VAR      = 6
    NUM_E    = 7

class BinOpType(Enum):
    PLUS     = 1
    MINUS    = 2
    MULTIPLY = 3
    DIVIDE   = 4
    EXPONENT = 5

    def __repr__(self) -> str:
        return self.name

@dataclass(frozen=True)
class Token:
    type: TokenType
    value: any = None

    def __eq__(self, __o: object) -> bool:
        if self.type == __o.type and self.value == __o.value:
            return True
        else:
            return False

    def __repr__(self):
        return self.type.name + (f" {self.value}" if self.value != None else "")


class AstNode:
    def __init__(self, tok= None, n = []):
        self.token = tok
        self.nexts = n if len(n) != 0 else []

    def __repr__(self) -> str:
        return self.token.__repr__() + " (" + " ".join( [child.__repr__() for child in self.nexts ] ) + ")"

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, AstNode):
            return False
        if self.token != __o.token:
            return False
        if not all([a == b for a,b in zip(self.nexts, __o.nexts)]):
            return False
        return True



def preParser(tokens):
    output_copy = [] 
    """
    conversions:
        5x -> 5*x
        xsin(x) -> x * sin(x)
        e^x -> exp(x)
    """

    if tokens[0].value == BinOpType.MINUS:
        output_copy.append(Token(TokenType.NUMBER, 0))

    for token in tokens:
        if len(output_copy) != 0:
            if token.type == TokenType.VAR:
                # check if there is a numer in front - patern 5x -> 5*x
                if output_copy[-1].type == TokenType.NUMBER:
                    output_copy.append( Token( TokenType.BINOP, BinOpType.MULTIPLY ))
                # patern: (...)x -> )*x
                elif output_copy[-1].type == TokenType.RPAREN:
                    output_copy.append( Token( TokenType.BINOP, BinOpType.MULTIPLY ))
            
            elif token.type == TokenType.FUNC:
                # patern 5sin -> 5*sin
                if output_copy[-1].type == TokenType.NUMBER:
                    output_copy.append( Token( TokenType.BINOP, BinOpType.MULTIPLY ))
                # xsin(x) -> x*sin(x)
                elif output_copy[-1].type == TokenType.VAR:
                    output_copy.append( Token( TokenType.BINOP, BinOpType.MULTIPLY ))

            elif token.value == BinOpType.MINUS:
                if output_copy[-1].type in (TokenType.BINOP, TokenType.LPEREN):
                    # turn a "-" without an left argument into
                    # -1  * 
                    output_copy.append(Token(TokenType.NUMBER, -1))
                    output_copy.append(Token(TokenType.BINOP, BinOpType.MULTIPLY))
                    continue

        output_copy.append(token)
    
    return output_copy



BinOpsOrder = [
    (BinOpType.PLUS, BinOpType.MINUS),
    (BinOpType.MULTIPLY, BinOpType.DIVIDE),
    (BinOpType.EXPONENT, None)
]




def Parser(tokens) -> AstNode:
    new_root = AstNode()
    parems_open = 0

    # if just one token
    if len(tokens) == 1:
        new_root.token = tokens[0]
        return new_root

    # handle +,-,*,/,^
    for curr_op in range(3):
        if curr_op != 2:
            for i, token in enumerate(reversed(tokens)):
                # since exponent is left associative list has to be rereversed TODO
                i = len(tokens) - i - 1
                
                # handle parems

                # skip numbers
                if token.type == TokenType.NUMBER:
                    continue

                if token.type == TokenType.RPAREN:
                    parems_open += 1
                    
                elif token.type == TokenType.LPEREN:
                    parems_open -= 1

                # find all operations
                if token.type == TokenType.BINOP and parems_open == 0:
                    # look for curr_op
                    if token.value in BinOpsOrder[curr_op]:
                        new_root.token = token
                        # add child nodes
                        # TODO
                        new_root.nexts.append( Parser( tokens[:i:] ) )
                        new_root.nexts.append( Parser( tokens[i+1::] ) )
                        return new_root

        # exponent since its right asociative
        else:
            for i, token in enumerate(tokens):

                # since exponent is left associative list has to be rereversed TODO
                
                # handle parems

                # skip numbers
                if token.type == TokenType.NUMBER:
                    continue

                if token.type == TokenType.RPAREN:
                    parems_open += 1
                    
                elif token.type == TokenType.LPEREN:
                    parems_open -= 1

                # find all operations
                if token.type == TokenType.BINOP and parems_open == 0:
                    # look for curr_op
                    if token.value in BinOpsOrder[curr_op]:
                        new_root.token = token
                        # add child nodes
                        # TODO
                        new_root.nexts.append( Parser( tokens[:i:] ) )
                        new_root.nexts.append( Parser( tokens[i+1::] ) )
                        return new_root


        if parems_open != 0:
            raise Exception("\nNot the same amout of open and closed parems\n")    

    # handle parenthesis
    # i think this can only mean that input is of form:  ( expresion )
    if tokens[0].type == TokenType.LPEREN:
        # remove the wraping parenthesis and parse the input
        return Parser(tokens[1:-1:])

    # handle functions - input sin( expression )
    if tokens[0].type == TokenType.FUNC:
        # set func node
        new_root.token = tokens[0]
        # add child node without the parenthesis
        new_root.nexts.append( Parser(tokens[2:-1:]) ) 
    return new_root


# converts AST into string
# need to pass empty array when calling from outside this func 
# major TODO
def deparser(node: AstNode) -> 'list[Token]':
    
    # basicly inorder tree search 
    token_list = []

    # nodes with no children
    if node.token.type in (TokenType.VAR, TokenType.CONST, TokenType.NUM_E, TokenType.NUMBER):
        if node.token.type == TokenType.NUMBER:
            if node.token.value < 0:
                return [Token(TokenType.LPEREN), node.token, Token(TokenType.RPAREN)]
        return [node.token]

    # nodes with one child
    if node.token.type == TokenType.FUNC:
        token_list.append(node.token)
        token_list.append( Token(TokenType.LPEREN))
        token_list += deparser(node.nexts[0])
        token_list.append( Token(TokenType.RPAREN))
        return token_list

    # node must be Binop

    #search left subtree
    left_list = deparser(node.nexts[0]) 

    #search right subtree
    right_list = deparser(node.nexts[1])

    # check if child node is lower in precedence than root node
    # if yes, add parethesis
    # propably a batter why to do this 
    childA = node.nexts[0]
    childB = node.nexts[1]
    
    if node.token.value == BinOpType.EXPONENT:
        # simplify a^-1 -> 1/a
        if childB.token.value == 1:
            token_list.append( Token(TokenType.NUMBER, 1))
            token_list.append(Token(TokenType.BINOP, BinOpType.DIVIDE))
            token_list.append(Token(TokenType.LPEREN))
            token_list += left_list
            token_list.append( Token(TokenType.RPAREN))
            return token_list

        # if child is an operation put it in parems
        if childA.token.type == TokenType.BINOP:
            token_list.append(Token(TokenType.LPEREN))
            token_list += left_list
            token_list.append( Token(TokenType.RPAREN))
        else:
            token_list += left_list
        
        # add this node to list
        token_list.append(node.token)

        # if child is an operation put it in parems
        if childB.token.type == TokenType.BINOP:
            token_list.append(Token(TokenType.LPEREN))
            token_list += right_list
            token_list.append( Token(TokenType.RPAREN))
        else:
            token_list += right_list
        
    elif node.token.value == BinOpType.MULTIPLY:
        # if child is an operation put it in parems
        if childA.token.value in (BinOpType.PLUS, BinOpType.MINUS):
            token_list.append(Token(TokenType.LPEREN))
            token_list += left_list
            token_list.append( Token(TokenType.RPAREN))
        else:
            token_list += left_list

        # add this node to list
        token_list.append(node.token)

         # if child is an operation put it in parems
        if childB.token.type in (BinOpType.PLUS, BinOpType.MINUS):
            token_list.append(Token(TokenType.LPEREN))
            token_list += right_list
            token_list.append( Token(TokenType.RPAREN))
        else:
            token_list += right_list

    # for now always put divide in parems
    elif node.token.value == BinOpType.DIVIDE:
        token_list.append(Token(TokenType.LPEREN))
        token_list += left_list
        token_list.append( Token(TokenType.RPAREN))
        
        # add this node to list
        token_list.append(node.token)

        token_list.append(Token(TokenType.LPEREN))
        token_list += right_list
        token_list.append( Token(TokenType.RPAREN))

    
    else: # plus and minus
        token_list += left_list
        token_list.append( node.token )
        token_list += right_list

    return token_list
        

# transforms list of tokens into output string
def delexer(token_list: 'list[Token]') -> str:
    out_list = []
    for token in token_list:
        if token.type == TokenType.LPEREN:
            out_list.append("(")
        elif token.type == TokenType.RPAREN:
            out_list.append(")")
        elif token.type == TokenType.NUM_E:
            out_list.append("e")
        elif token.type == TokenType.NUMBER:
            out_list.append(str(token.value))
        elif token.type == TokenType.FUNC:
            out_list.append(token.value)
        elif token.type == TokenType.VAR:
            out_list.append(token.value)
        # only binops left
        elif token.value == BinOpType.PLUS:
            out_list.append("+")
        elif token.value == BinOpType.MINUS:
            out_list.append("-")
        elif token.value == BinOpType.MULTIPLY:
            out_list.append("*")
        elif token.value == BinOpType.DIVIDE:
            out_list.append("/")
        elif token.value == BinOpType.EXPONENT:
            out_list.append("^")

    return "".join(out_list)


# reverses all non intuative changes made by cleanup
# TODO not urgent
# perhaps change it so it works on token list
def uncleanup(token_list: "list[Token]"):

    # patterns elem is tuple ([ nodes ], [nodes])
    patterns = [

        ([  # " -1 * " ->  " - "
        Token(TokenType.LPEREN), 
        Token(TokenType.NUMBER, -1),
        Token(TokenType.RPAREN),
        Token(TokenType.BINOP, BinOpType.MULTIPLY)
        ], [Token(TokenType.BINOP, BinOpType.MINUS)]),
        
        ([  # " + - " ->  " - "
            Token(TokenType.BINOP, BinOpType.PLUS), 
            Token(TokenType.BINOP, BinOpType.MINUS),
        ], [Token(TokenType.BINOP, BinOpType.MINUS)])

    ]

    in_list = token_list
    out_list = []
    change_made = True
    # match pattern to list of tokens
    while True:
        change_made = False
        for pattern1, evaluates_to in patterns:
            for i, token in enumerate(in_list):
                # (-1)* -> -
                if token.type == TokenType.LPEREN:
                    if all([tok == pattern_tok for tok, pattern_tok in zip(in_list[i::], pattern1)]):
                        out_list += in_list[0:i:]
                        out_list += evaluates_to
                        out_list += in_list[ i + len(pattern1):: ]
                        change_made = True
                        break
                
        if not change_made:
            return in_list

        in_list = copy.deepcopy(out_list)
        out_list = []


class Lexer:
    def __init__(self, text):
        self.text = iter(text)
        self.advance()
        self.tokens = []

    def advance(self):
        try:
            self.curent_char = next(self.text)
        except StopIteration:
            self.curent_char = None

    def generate_num(self):
        decimal_point_count = 0
        if self.curent_char == ".":
            decimal_point_count = 1

        numer_str = self.curent_char
        self.advance()

        while self.curent_char != None and (self.curent_char in DIGITS or self.curent_char == "."):
            # count decimal points
            if self.curent_char == ".":
                decimal_point_count += 1
                if decimal_point_count == 2:
                    break
                    # TODO maybe raise RuntimeError

            numer_str += self.curent_char
            self.advance()

        if numer_str[0] == ".":
            numer_str = "0" + numer_str
        if numer_str[-1] == ".":
            numer_str += "0"

        return Token(TokenType.NUMBER, float(numer_str)) 

    def generate_function(self):
        f_name = ""
        while self.curent_char != "(":
            if self.curent_char == None:
                raise Exception(f"Ileagal phrase {f_name}")

            f_name += self.curent_char
            self.advance()
        if f_name not in FUNC_NAMES:
            raise Exception(f"Ileagal func name {f_name}")
        return Token(TokenType.FUNC, f_name)


    # takes argument var which is the unknow with respect to which to differantiate
    def generate_tokens(self):
        while self.curent_char != None:
            
            # TODO doensnt work
            if self.curent_char in WHITESPACE:
                self.advance()
                continue
            
            if self.curent_char in DIGITS or self.curent_char == '.':
                self.tokens.append( self.generate_num() )
                continue

            if self.curent_char == "+":
                self.tokens.append( Token(TokenType.BINOP, BinOpType.PLUS))
    
            elif self.curent_char == "e":
                self.tokens.append( Token( TokenType.NUM_E))

            elif self.curent_char == "-":
                self.tokens.append( Token(TokenType.BINOP, BinOpType.MINUS))
    
            elif self.curent_char == "*":
                self.tokens.append( Token(TokenType.BINOP, BinOpType.MULTIPLY))
    
            elif self.curent_char == "/":
                self.tokens.append( Token(TokenType.BINOP, BinOpType.DIVIDE))

            elif self.curent_char == "^":
                self.tokens.append( Token(TokenType.BINOP, BinOpType.EXPONENT))
        
            elif self.curent_char == "(":
                self.tokens.append( Token(TokenType.LPEREN))

            elif self.curent_char == ")":
                self.tokens.append( Token(TokenType.RPAREN))

            elif self.curent_char in VAR_NAME:
                self.tokens.append( Token(TokenType.VAR, self.curent_char))
            
            # unknow character - function
            else:
                # maybe function - build fucnton - or const - TODO later
                self.tokens.append(self.generate_function())
                continue

            self.advance()

        return self.tokens


    