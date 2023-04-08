from keys import (alternative, Rparen, Rbracket,
                    Rbrace, dot, epsilon,
                    Lparen, Lbracket, Lbrace,
                    optional, kleene, symbols, plus, hash, elevated)
from Node import Node
import pydot
import networkx as nx
import matplotlib.pyplot as plt

class ExpressionTree:
    def __init__(self, r):
        self.r = r
        self.tree = None
        self.lastChar = None
        self.postfix = []
        self.symbols = []
        # Precedencias de los operadores
        self.precedence = {
            alternative: 1,
            dot: 2,
            optional: 3,
            kleene: 3
        }
        # Funciones calculadas a partir del árbol sintáctico
        self.nodes = {}
        self.nullable = {}
        self.firstpos = {}
        self.lastpos = {}
        self.nextpos = {}
        # Stack del AFN
        self.stack = []


    def is_empty(self):
        return len(self.stack) == 0

    def last(self):
        return self.stack[-1]

    def pop(self):
        if not self.is_empty():
            return self.stack.pop()
        else:
            BaseException("Error")

    def push(self, op):
        self.stack.append(op)

    def checkExpression(self):
        operators = {kleene, plus, optional, alternative, elevated}
        stack = []
        for i, token in enumerate(self.r):
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
                if self.r[i - 1] in {kleene, optional, elevated}:
                    raise ValueError(f"Invalid use of {token} at position {i}")
            elif token in operators-{alternative}:
                if i == 0 or self.r[i - 1] in operators.union({Lparen, Lbrace, Lbracket, alternative}):
                    raise ValueError(f"Invalid use of {token} at position {i}")
                elif token == '^' and i != 1:
                    raise ValueError(f"Invalid use of {token} at position {i}")
                elif token == kleene and self.r[i - 1] in operators.union({Lparen}) and self.r[i - 1] != alternative:
                    raise ValueError(f"Invalid use of {token} at position {i}")
                elif token == '+' and self.r[i - 1] in operators.union({Lparen}) and self.r[i - 1] != alternative:
                    raise ValueError(f"Invalid use of {token} at position {i}")
                elif token == optional and self.r[i - 1] in operators.union({Lparen}) and self.r[i - 1] != alternative:
                    raise ValueError(f"Invalid use of {token} at position {i}")
            elif token == alternative:
                if i == 0 or i == len(self.r) - 1:
                    raise ValueError(f"Invalid use of {token} at position {i}")
                elif self.r[i - 1] in operators.union({alternative, Lparen})-{kleene, optional, plus}:
                    raise ValueError(f"Invalid use of {token} at position {i}")
                elif self.r[i + 1] in operators.union({Rparen, alternative}):
                    raise ValueError(f"Invalid use of {token} at position {i}")
        if stack:
            opening_token, opening_index = stack.pop()
            raise ValueError(
                f"Unbalanced {opening_token} at position {opening_index}")
        else:
            self.r = self.r.replace('∗', kleene)
            return True

    def replaceOperators(self):
        i = 0
        while i < len(self.r):
            if self.r[i] == optional and self.r[i-1] != Rparen:
                self.r = self.r[:i-1] + Lparen + self.r[i-1] + \
                    alternative + epsilon + Rparen + self.r[i+1:]
            elif self.r[i] == optional and self.r[i-1] == Rparen:
                if self.r[i-3] == alternative:
                    self.r = self.r[:i] + \
                        alternative + epsilon + self.r[i+1:]
                else:
                    self.r = self.r[:i-1] + alternative + \
                        epsilon + self.r[i-1] + self.r[i+1:]
            elif self.r[i] == plus:
                if self.r[i-1] == Rparen:
                    j = i - 2
                    paren_count = 1
                    while j >= 0:
                        if self.r[j] == Rparen:
                            paren_count += 1
                        elif self.r[j] == Lparen:
                            paren_count -= 1
                        if paren_count == 0:
                            break
                        j -= 1
                    if j >= 0:
                        replacement = self.r[j+1:i-1]
                        self.r = self.r[:j+1] + replacement + Rparen + \
                            Lparen + replacement + Rparen + \
                            kleene + self.r[i+1:]
                        i += len(replacement) + 3
                    else:
                        raise ValueError(
                            f"Invalid use of {plus} at position {i}")
                else:
                    self.r = self.r[:i] + \
                        self.r[i-1] + kleene + self.r[i+1:]
            i += 1

    def augmentr(self):
        self.r = self.r + hash + dot


    def getPrecedence(self, i):
        try:
            return self.precedence[i] <= self.precedence[self.last()]
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
        while (not self.is_empty() and self.getPrecedence(c)):
            self.postfix.append(self.pop())
        self.push(c)

    def processToken(self, c):
        if c in [*symbols, Lparen, Lbracket, Lbrace]:
            while (not self.is_empty() and self.last() in [optional, kleene]):
                self.postfix.append(self.pop())
        if c in symbols:
            self.postfix.append(c)
        elif c in [Lparen, Lbracket, Lbrace]:
            self.push(c)
        elif c == Rparen:
            while not self.is_empty() and self.last() != Lparen:
                a = self.pop()
                self.postfix.append(a)
            if self.is_empty() or self.last() != Lparen:
                BaseException("Error")
            else:
                self.pop()
        elif c == Rbracket:
            while not self.is_empty() and self.last() != Lbracket:
                a = self.pop()
                self.postfix.append(a)
            if self.is_empty() and self.last() != Lbracket:
                BaseException("Error")
            else:
                self.pop()
                self.processOper(kleene)
        elif c == Rbrace:
            while not self.is_empty() and self.last() != Lbrace:
                a = self.pop()
                self.postfix.append(a)
            if self.is_empty() and self.last() != Lbrace:
                BaseException("Error")
            else:
                self.pop()
                self.processOper(optional)
        else:
            self.processOper(c)
        self.lastChar = c

    def toPostfix(self):
        self.lastChar = None
        for c in self.r:
            self.concatOP(c)
            self.processToken(c)
        while not self.is_empty():
            self.postfix.append(self.pop())

    def genTree(self, node: Node, i=0):
        if node:
            i = self.genTree(node.left, i)
            i = self.genTree(node.right, i)
            node.id = i
            self.nodes[i] = node.value
            # Se calcula el valor de nullable(n), firstpos(n) y lastpos(n)
            if node.value == epsilon:
                self.nullable[node.id] = True
                self.firstpos[node.id] = []
                self.lastpos[node.id] = []
            elif node.value in symbols:
                self.nullable[node.id] = False
                self.firstpos[node.id] = [node.id]
                self.lastpos[node.id] = [node.id]
            elif node.value == alternative:
                self.nullable[node.id] = self.nullable[node.left.id] or self.nullable[node.right.id]
                self.firstpos[node.id] = [
                    *self.firstpos[node.left.id], *self.firstpos[node.right.id]]
                self.lastpos[node.id] = [
                    *self.lastpos[node.left.id], *self.lastpos[node.right.id]]
            elif node.value == dot:
                self.nullable[node.id] = self.nullable[node.left.id] and self.nullable[node.right.id]
                self.firstpos[node.id] = [*self.firstpos[node.left.id], *self.firstpos[node.right.id]
                                        ] if self.nullable[node.left.id] else self.firstpos[node.left.id]
                self.lastpos[node.id] = [*self.lastpos[node.left.id], *self.lastpos[node.right.id]
                                        ] if self.nullable[node.right.id] else self.lastpos[node.right.id]
            elif node.value in [kleene, optional]:
                self.nullable[node.id] = True
                self.firstpos[node.id] = self.firstpos[node.left.id]
                self.lastpos[node.id] = self.lastpos[node.left.id]
            if node.value == dot:
                for lastpos in self.lastpos[node.left.id]:
                    if lastpos in self.nextpos.keys():
                        self.nextpos[lastpos] = list(dict.fromkeys([
                            *self.nextpos[lastpos], *self.firstpos[node.right.id]]))
                    else:
                        self.nextpos[lastpos] = self.firstpos[node.right.id]
                    self.nextpos[lastpos].sort()
            elif node.value == kleene:
                if node.left is not None:
                    for lastpos in self.lastpos[node.left.id]:
                        if lastpos in self.nextpos.keys():
                            self.nextpos[lastpos] = list(dict.fromkeys([
                                *self.nextpos[lastpos], *self.firstpos[node.left.id]]))
                        else:
                            self.nextpos[lastpos] = self.firstpos[node.left.id]
                        self.nextpos[lastpos].sort()
            # Transiciones epsilon del arbol
            if self.nullable[node.id]:
                self.nodes[node.id] = epsilon
            return i + 1
        return i


    def getTree(self):
        for c in self.postfix:
            if c in symbols:
                self.push(Node(c))
            else:
                op = Node(c)
                if c in [optional, kleene]:
                    x = self.pop()
                else:
                    y = self.pop()
                    x = self.pop()
                    op.right = y
                op.left = x
                self.push(op)
        self.tree = self.pop()
        self.genTree(self.tree)

    def search_by_id(self, id):
        if id in self.nodes.keys():
            return self.nodes[id]
        return None

    def draw_tree(self, node=None, G=None, pos=None):
        if G is None:
            G = nx.DiGraph()
            pos = {}
        if node is None:
            node = self.tree
        if node:
            G.add_node(node.id, label=node.value)
            pos[node.id] = (node.id, -node.id)
            if node.left:
                G.add_edge(node.id, node.left.id)
                self.draw_tree(node.left, G, pos)
            if node.right:
                G.add_edge(node.id, node.right.id)
                self.draw_tree(node.right, G, pos)
        if node == self.tree:
            labels = nx.get_node_attributes(G, 'label')
            nx.draw(G, pos, with_labels=True, labels=labels, node_size=100, node_color='skyblue')
            plt.show()
