import lexer
from derivator import derivator, cleanup
#import Myparser

text = input("Calc: ")
l = lexer.Lexer(text)
tokens = l.generate_tokens()
tokens = lexer.preParser(tokens)

node = lexer.Parser(tokens)
a = derivator(node)

# a = lexer.AstNode()
# b = lexer.AstNode()
# c = lexer.AstNode()

# a.token = lexer.Token( lexer.TokenType.BINOP, lexer.BinOpType.DIVIDE )
# a.nexts = [b, c]
# b.token = lexer.Token( lexer.TokenType.NUMBER, 0.0 )
# c.token = lexer.Token( lexer.TokenType.FUNC, 'sin' )


a = cleanup(a)

print(a)

