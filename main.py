from ExceptionClass import myException
import lexer
from derivator import derivator, cleanup
from ExceptionClass import myException

text = input("Calc: ")
try:
    l = lexer.Lexer(text)
    tokens = l.generate_tokens()
    tokens = lexer.preParser(tokens)
    a = lexer.Parser(tokens)
    a = cleanup(a)
    a = derivator(a)
    a = cleanup(a)
    a = lexer.deparser(a)
    a = lexer.uncleanup(a)
    a = lexer.delexer(a)

except myException as ex:
    print("Invalid Input")
    print(ex.text)
    good_toks = lexer.delexer(ex.tokens)
    if len(good_toks) != 0:
        print(good_toks, "_")
        print(" "*len(good_toks)+"^ error around here")
    
    exit(-69)


print( "d/dx ( " + text +  " )\n", "Evaluates to:\n",  a)

