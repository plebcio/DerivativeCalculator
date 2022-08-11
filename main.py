import lexer
from derivator import derivator, cleanup #simplify
#import Myparser

text = input("Calc: ")
l = lexer.Lexer(text)
tokens = l.generate_tokens()
tokens = lexer.preParser(tokens)

a = lexer.Parser(tokens)
a = derivator(a)

# a = lexer.AstNode()
# b = lexer.AstNode()
# c = lexer.AstNode()

# a.token = lexer.Token( lexer.TokenType.BINOP, lexer.BinOpType.DIVIDE )
# a.nexts = [b, c]
# b.token = lexer.Token( lexer.TokenType.NUMBER, 0.0 )
# c.token = lexer.Token( lexer.TokenType.FUNC, 'sin' )


a = cleanup(a)

print(a)

