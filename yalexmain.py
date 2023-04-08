from ExpressionTree import *
from AFN import *
from AFD import *
from yalx import *

while True:
    file_name = input("Enter the name of the yalex file to process (slr-1/slr-2/slr-3/slr-4) or type 'exit' to quit: ")
    if file_name == 'exit':
        print('\n\nGoodbye!\n\n')
        break
    
    path = '' + file_name + '.yal'
    yal_processor = YalProcessor(path)
    
    for rule_name in yal_processor.rules:
        print(rule_name, yal_processor.rules[rule_name])
        
        expr_tree = ExpressionTree(yal_processor.rules[rule_name])
        expr_tree.checkExpression()
        expr_tree.replaceOperators()
        expr_tree.toPostfix()
        
        print('Postfix notation:', ''.join(expr_tree.postfix))
        
        expr_tree.getTree()
        expr_tree.draw_tree()
        print('\n\n')

