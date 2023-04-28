from Functions import *
Lparen = '('
Rparen = ')'
Lbracket = '{'
Rbracket = '}'
Lbrace = '['
Rbrace = ']'
groupers = [Lparen, Rparen, Lbracket, Rbracket, Lbrace, Rbrace]
alternative = '|'
dot = '•'
minus ='-'
optional = '?'
kleene = '∗'
plus = '+'
elevated = '^'
operators = [alternative, dot, optional, kleene, plus]
epsilon = 'ε'
hash = '#'


operator_symbols = [plus, minus, '*', '/']
symbols = [replace_reserved_words(chr(i)) for i in range(1, 255) if chr(i) not in operators]
symbols += epsilon
alphabet = [*symbols, *operators, *groupers, epsilon]