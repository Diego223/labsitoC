from regularExpression import *
from ExpressionTree import *
from AFN import *
from AFD import *
from yalx import *


def to_regex(rule_body):
        regex_rule = ""
        i = 0
        Lbrace = '['
        Rbrace = ']'

        while i < len(rule_body):
            if rule_body[i] == Lbrace:
                i += 1
                inside_brackets = ""
                while rule_body[i] != Rbrace:
                    inside_brackets += rule_body[i]
                    i += 1
                expression = inside_brackets.split("''")
                operands = [] 
                for exp in expression:
                    operands.append(exp)

                regex_rule += "(" + "|".join(operands) + ")"
            else:
                regex_rule += rule_body[i]

            i += 1

        return regex_rule



def separate_symbols(regex_rule):
    regex_rule = regex_rule.replace("('+|-')", "('+'|'-')")
    return regex_rule


def main():
    while True:
        file_name = input("Enter the name of the yalex file to process (slr-1/slr-2/slr-3/slr-4) or exit: ")
        if file_name == 'exit':
            print('\n\nSaliste\n\n')
            break
        path = '' + file_name + '.yal'
        yal_processor = YalProcessor(path)

        # for rule_name in yal_processor.rules:
        #     rule_body = yal_processor.rules[rule_name]

        #     regex = to_regex(rule_body)
        #     regex = separate_symbols(regex)

        #     print(rule_name, regex)
        #     expr_tree = regularExpression(regex)
        #     print('Postfix notation:', ''.join(expr_tree.postfix))
        #     tree = ExpressionTree(expr_tree.postfix)
        #     print('\n\n')

if __name__ == "__main__":
    main()
