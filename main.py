import lexer
from derivator import derivator, cleanup

text = input("Calc: ")
l = lexer.Lexer(text)
tokens = l.generate_tokens()
tokens = lexer.preParser(tokens)


a = lexer.Parser(tokens)
a = derivator(a)
a = cleanup(a)
a = lexer.deparser(a)
a = lexer.uncleanup(a)
a = lexer.delexer(a)

print( "d/dx ( " + text +  " )\n", "Evaluates to:\n",  a)

