"""
codes: 0: num, 1: bianryOp1 (+, -), 2: bianryOp2 (*, /), 3: bianryOp3 ( ^ ), 4: parems '()',  5: uniaryOp ( sin, exp, log, ln  )
"""
VAR_NAME = ["x", "y", "z"]

from dataclasses import dataclass
from enum import Enum
from re import S

WHITESPACE = " \t\n"
DIGITS = "0123456789"

FUNC_NAMES = ['sin', 'cos', 'exp', 'arcsin', "sqrt", "ln"]

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
def deparser(node: AstNode) -> str:
    pass


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


    