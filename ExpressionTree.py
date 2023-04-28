from Node import Node
from keys import *
from graphviz import Digraph
from Functions import *

class ExpressionTree:
    def __init__(self, postfix):
        self.postfix = postfix
        self.tree = None
        self.symbols = []
        self.nodes = {}
        self.nullable = {}
        self.firstpos = {}
        self.lastpos = {}
        self.nextpos = {}
        self.stack = []
        self.getTree()
        self.getSymbols()

    def getSymbols(self):
        for symbol in self.postfix:
            if symbol in symbols and symbol != hash and symbol not in self.symbols:
                self.symbols.append(symbol)

#*************************************************************************** GEN ARBOL
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
            # Se calcula el valor de nextpos(n)
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
            # print(c)
            if c in symbols:
                push(self.stack, Node(c))
            else:
                op = Node(c)
                if c in [optional, kleene]:
                    x = pop(self.stack)
                else:
                    y = pop(self.stack)
                    x = pop(self.stack)
                    op.right = y
                op.left = x
                push(self.stack, op)
        self.tree = pop(self.stack)
        self.genTree(self.tree)

    def search_by_id(self, id):
        if id in self.nodes.keys():
            return self.nodes[id]
        return None

    def showTable(self, node=None):
        if node is None:
            node = self.tree
            self.dot = Digraph('Expression Tree', format='pdf')
            self.dot.attr(rankdir='TB')
            self.dot.attr('node', shape='circle')
        if node.left:
            left_node_name = f"{node.left.value}_{node.left.id}"
            left_node_label = ''.join(['\\\\' if c == '\\' else c for c in str(node.left.value)])
            self.dot.node(left_node_name, left_node_label)  
            self.dot.edge(f"{node.value}_{node.id}", left_node_name)
            self.showTable(node.left)
        if node.right:
            right_node_name = f"{node.right.value}_{node.right.id}"
            right_node_label = ''.join(['\\\\' if c == '\\' else c for c in str(node.right.value)])
            self.dot.node(right_node_name, right_node_label)  
            self.dot.edge(f"{node.value}_{node.id}", right_node_name)
            self.showTable(node.right)
        if node.id == self.tree.id:
            tree_node_name = f"{node.value}_{node.id}"
            tree_node_label = ''.join(['\\\\' if c == '\\' else c for c in str(node.value)])
            self.dot.node(tree_node_name, tree_node_label)
            self.dot.render('Graphs/ExpressionTree', view=True)
