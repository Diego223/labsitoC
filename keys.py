Lparen = '('
Rparen = ')'
Lbracket = '{'
Rbracket = '}'
Lbrace = '['
Rbrace = ']'
alternative = '|'
dot = '•'
optional = '?'
kleene = '*'
plus = '+'
elevated = '^'
operators = [alternative, dot, optional, kleene, plus]
epsilon = 'ε'
hash = '#'

def replace_reserved_words(r: str):
    return (r
            .replace('(', 'β')
            .replace(')', 'δ')
            .replace('{', 'ζ')
            .replace('}', 'η')
            .replace('[', 'θ')
            .replace(']', 'ω')
            .replace('|', 'φ')
            )


symbols = [replace_reserved_words(chr(i)) for i in range(1, 255) if chr(i) not in operators]
symbols += epsilon