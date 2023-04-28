from keys import *
from Functions import *

class regularExpression:
    def __init__(self, regex, flag = False):
        self.regex = regex
        self.lastChar = None
        self.postfix = []
        # Precedencias de los operadores
        self.precedence = {
            alternative: 1,
            dot: 2,
            optional: 3,
            kleene: 3
        }
        self.stack = []
        self.checkExpression()
        self.regex = process_string(self.regex)
        self.expandExp()
        self.regex = process_string(self.regex)
        # print("post processing", self.regex)
        self.replaceOperators()
        self.toPostfix()

#*******************************BALANCEO************************************
    def checkExpression(self):
        operators = {kleene, plus, optional, alternative}
        stack = []
        inQuotes = False
        for i, token in enumerate(self.regex):
            if token == "'":
                inQuotes = not inQuotes
            if inQuotes:
                continue
            if token in '([{':
                stack.append((token, i))
            elif token in ')]}':
                if not stack:
                    raise ValueError(f"Unbalanced {token} at position {i}")
                opening_token, opening_index = stack.pop()
                if (opening_token == Lparen and token != Rparen) or \
                    (opening_token == Lbrace and token != Rbrace) or \
                        (opening_token == Lbracket and token != Rbracket):
                    raise ValueError(
                        f"Mismatched {opening_token} and {token} at positions {opening_index} and {i}")
            elif token == plus:
                if i == 0:
                    raise ValueError(f"Invalid use of {token} at position {i}")
                if self.regex[i - 1] in {kleene, optional}:
                    raise ValueError(f"Invalid use of {token} at position {i}")
            elif token in operators-{alternative}:
                if i == 0 or self.regex[i - 1] in operators.union({Lparen, Lbrace, Lbracket, alternative}):
                    raise ValueError(f"Invalid use of {token} at position {i}")
                elif token == '^' and i != 1:
                    raise ValueError(f"Invalid use of {token} at position {i}")
                elif token == kleene and self.regex[i - 1] in operators.union({Lparen}) and self.regex[i - 1] != alternative:
                    raise ValueError(f"Invalid use of {token} at position {i}")
                elif token == '+' and self.regex[i - 1] in operators.union({Lparen}) and self.regex[i - 1] != alternative:
                    raise ValueError(f"Invalid use of {token} at position {i}")
                elif token == optional and self.regex[i - 1] in operators.union({Lparen}) and self.regex[i - 1] != alternative:
                    raise ValueError(f"Invalid use of {token} at position {i}")
            elif token == alternative:
                if i == 0 or i == len(self.regex) - 1:
                    raise ValueError(f"Invalid use of {token} at position {i}")
                elif self.regex[i - 1] in operators.union({alternative, Lparen})-{kleene, optional, plus}:
                    raise ValueError(f"Invalid use of {token} at position {i}")
                elif self.regex[i + 1] in operators.union({Rparen, alternative}):
                    raise ValueError(f"Invalid use of {token} at position {i}")
        if stack:
            opening_token, opening_index = stack.pop()
            raise ValueError(
                f"Unbalanced {opening_token} at position {opening_index}")
        else:
            self.regex = self.regex.replace('∗', kleene)
            return True

    def replaceOperators(self):
        i = 0
        while i < len(self.regex):
            # Manejo de casos especiales de ?
            if self.regex[i] == optional and self.regex[i-1] != Rparen:
                self.regex = self.regex[:i-1] + Lparen + self.regex[i-1] + \
                    alternative + epsilon + Rparen + self.regex[i+1:]
            elif self.regex[i] == optional and self.regex[i-1] == Rparen:
                # Si tenemos una operacion dentro  ((a|t)?) solo convertimos ? a |ε
                if self.regex[i-3] == alternative:
                    self.regex = self.regex[:i] + \
                        alternative + epsilon + self.regex[i+1:]
                # si solo hay un operando o una cerradura de kleene simple como (a)? o (a*)?
                else:
                    self.regex = self.regex[:i-1] + alternative + \
                        epsilon + self.regex[i-1] + self.regex[i+1:]
            # Manejo de casos especiales de + +
            elif self.regex[i] == plus:
                if self.regex[i-1] == Rparen:
                    j = i - 2
                    paren_count = 1
                    while j >= 0:
                        if self.regex[j] == Rparen:
                            paren_count += 1
                        elif self.regex[j] == Lparen:
                            paren_count -= 1
                        if paren_count == 0:
                            break
                        j -= 1
                    if j >= 0:
                        replacement = self.regex[j+1:i-1]
                        self.regex = self.regex[:j+1] + replacement + Rparen + \
                            Lparen + replacement + Rparen + \
                            kleene + self.regex[i+1:]
                        i += len(replacement) + 3
                    else:
                        raise ValueError(
                            f"Invalid use of {plus} at position {i}")
                else:
                    self.regex = self.regex[:i] + \
                        self.regex[i-1] + kleene + self.regex[i+1:]
            i += 1

    def augmentRegex(self):
        self.postfix.append(hash)
        self.postfix.append(dot)

    def expandExp(self):
        expanded = []
        i = 0
        special_vowels = {'a': 'á', 'e': 'é', 'i': 'í', 'o': 'ó', 'u': 'ú', 'A': 'Á', 'E': 'É', 'I': 'Í', 'O': 'Ó', 'U': 'Ú'}
        while i < len(self.regex):
            #expand range of characters
            if self.regex[i] == "\\" and i + 1 < len(self.regex) and self.regex[i + 1] in ["t", "n"]:
                expanded.append(self.regex[i:i + 2])
                i += 2
                continue
            if i + 2 < len(self.regex) and self.regex[i + 1] == minus:
                start_char = self.regex[i]
                end_char = self.regex[i + 2]
                if (start_char.isupper() and end_char.isupper()) or (start_char.islower() and end_char.islower()) or (start_char.isdigit() and end_char.isdigit()):
                    for char_code in range(ord(start_char), ord(end_char) + 1):
                        # if last character, don't append |
                        if char_code == ord(end_char):
                            expanded.append(chr(char_code))
                        else:
                            #if char is in vowels dictionary keys, also append its special vowels
                            if chr(char_code) in special_vowels.keys(): 
                                for vow in special_vowels[chr(char_code)]:
                                    expanded.append(chr(char_code) + alternative + vow + alternative)
                            else:
                                expanded.append(chr(char_code) + alternative)
                else:
                    expanded.append(self.regex[i])
                i += 3
            #expand groups of characters
            if i + 1 < len(self.regex) and self.regex[i] == '^':
                #^o will be operators
                if self.regex[i + 1] == 'o':
                    for o in operator_symbols:
                        # if last character, don't append |
                        if o == last(operator_symbols):
                            expanded.append(f"'{o}'")
                        else:
                            expanded.append(f"'{o}'" + alternative)
                #^g will be groupers
                elif self.regex[i + 1] == 'g':
                    for g in groupers:
                        # if last character, don't append |
                        if g == last(groupers):
                            expanded.append(f"'{g}'")
                        else:
                            expanded.append(f"'{g}'" + alternative)
                #^a will be any of the alphabet
                elif self.regex[i + 1] == 'a':
                    for a in alphabet:
                        # if last character, don't append |
                        if a == last(alphabet):
                            expanded.append(f"'{a}')")
                        if a == alphabet[0]:
                            expanded.append(f"('{a}'" + alternative)
                        else:
                            expanded.append(f"'{a}'" + alternative)
                i += 2
            else:
                expanded.append(self.regex[i])
                i += 1
        self.regex = ''.join(expanded)

#*******************************POSTFIX************************************
    def getPrecedence(self, i):
        try:
            return self.precedence[i] <= self.precedence[last(self.stack)]
        except:
            BaseException("Error")

    def concatOP(self, c):
        # If the following character is a symbol, a (, a {, or a [,
        # and the previous character was a symbol, a ), a }, a ], a ?, or a *.
        if (c in [*symbols, Lparen, Lbracket, Lbrace, plus] and
                self.lastChar in [*symbols, Rparen, Rbracket, Rbrace, optional, kleene]):
            # If the last character was a Kleene star, process it before adding the dot operator.
            if self.lastChar == kleene and c == kleene:
                self.processToken(kleene)
            self.processToken(dot)

    def processOper(self, c):
        # Se agrega a postfix hasta que haya un operador con menor jerarquía en el stack
        while (not is_empty(self.stack) and self.getPrecedence(c)):
            self.postfix.append(pop(self.stack))
        push(self.stack, c)

    def processToken(self, c):
        # Si es algun simbolo o un ( o { o [ se extraen todos los operadores de un solo simbolo ? o *
        if c in [*symbols, Lparen, Lbracket, Lbrace]:
            while (not is_empty(self.stack) and last(self.stack) in [optional, kleene]):
                self.postfix.append(pop(self.stack))
        if c in symbols:
            self.postfix.append(c)
        elif c in [Lparen, Lbracket, Lbrace]:
            push(self.stack, c)
        elif c == Rparen:
            while not is_empty(self.stack) and last(self.stack) != Lparen:
                a = pop(self.stack)
                self.postfix.append(a)
            if is_empty(self.stack) or last(self.stack) != Lparen:
                BaseException("Error")
            else:
                pop(self.stack)
        elif c == Rbracket:
            while not is_empty(self.stack) and last(self.stack) != Lbracket:
                a = pop(self.stack)
                self.postfix.append(a)
            if is_empty(self.stack) and last(self.stack) != Lbracket:
                BaseException("Error")
            else:
                pop(self.stack)
                self.processOper(kleene)
        elif c == Rbrace:
            while not is_empty(self.stack) and last(self.stack) != Lbrace:
                a = pop(self.stack)
                self.postfix.append(a)
            if is_empty(self.stack) and last(self.stack) != Lbrace:
                BaseException("Error")
            else:
                pop(self.stack)
                self.processOper(optional)
        else:
            self.processOper(c)
        self.lastChar = c

    def toPostfix(self):
        self.lastChar = None
        for c in self.regex:
            self.concatOP(c)
            self.processToken(c)
        while not is_empty(self.stack):
            self.postfix.append(pop(self.stack))
