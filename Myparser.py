from dataclasses import dataclass
from lexer import Token, TokenType, BinOpType

@dataclass
class AstNode:
    token: Token
    def __init__(self) -> None:
        self.nexts = []

# OPERATIONS = [TokenType.BINOP -> +,- ; *,/ ; ^, (), funcs]

BinOpsOrder = [
    (BinOpType.PLUS, BinOpType.MINUS),
    (BinOpType.MULTIPLY, BinOpType.DIVIDE),
    BinOpType.EXPONENT
]

def Parser(tokens):
    new_root = AstNode()
    parems_open = 0
    curr_op = 0
    while (1):
        for i, token in enumerate(tokens):
            # handle parems
            if token.type == TokenType.RPAREN:
                parems_open += 1
                
            elif token.type == TokenType.LPEREN:
                parems_open -= 1

            # not inside parems
            elif parems_open == 0:
                # found all operations
                if curr_op < 3 and token.type == TokenType.BINOP:
                    # look for curr_op
                    if token.value in BinOpsOrder[curr_op]:
                        new_root.token = token
                        # add child nodes
                        #new_root.nexts.append( parser( tokens[:i:] ) )
                        #new_root.nexts.append( parser( tokens[i+1::] ) )
                        return new_root


        # move onto next operation
        curr_op += 1
        if parems_open != 0:
            raise Exception("\nNot the same amout of open and closed parems\n")        