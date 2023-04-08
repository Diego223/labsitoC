import functools
import timeit
from AFN import AFN
from ExpressionTree import ExpressionTree
from AFD import *
from AFD import AFD



def timemeasure(func):
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        tinicial = timeit.default_timer()
        resultado = func(*args, **kwargs)
        tfinal = timeit.default_timer()
        print("Tiempo transcurrido: ", tfinal - tinicial, " segundos")
        return resultado
    return new_func


@timemeasure
def thompson_algorithm(regular_expression: str):
    # Generacion del syntax tree para debido NFA
    expression_tree = ExpressionTree(regular_expression)
    if (expression_tree.checkExpression()):
        expression_tree.replaceOperators()
        expression_tree.generate_postfix()
        expression_tree.generate_tree()
        nfa = AFN()
        nfa.generate_AFN_from_re(expression_tree)
        print(nfa)
        #nfa.graph_AFN()


        
        #NFA TO DFA ALGORITHM

        dfa = AFD(nfa)  
        print(dfa)
        dfa.nfa_to_dfa() 
        dfa.showDFA()

        # Apply DFA minimization

        #dfa.minimize()
        #dfa.showDFA()
        
        #DIRECT DFA 



        opcion =''
        # Simulacion
        while opcion != '1' and opcion !='2':    
            opcion = input('\n 1. Simular DFA \n 2. Simular NFA \n opcion: ')    
            if (opcion =='1'):
                Verificador = ""
                while Verificador != 'salir':
                    Verificador = input("\nIngrese la cadena a revisar o escriba 'salir' ")
                    if Verificador != 'salir':
                        result = dfa.simulate_dfa(Verificador)
                        print(f"'{Verificador}' {'Es correcto!, pertenece' if result else 'Es incorrecto! : ('}")
                    else:
                        print('\n\n')
                        break
            if (opcion =='2'):
                Verificador = ""
                while Verificador != 'salir':
                    Verificador = input("\nIngrese la cadena a revisar o escriba 'salir' : ")
                    if Verificador != 'salir':
                        result = nfa.simulate_afn(Verificador)
                        print(f"'{Verificador}' {'Es correcto!, pertenece' if result else 'Es incorrecto! : '}")
                    else:
                        print('\n\n')
                        break

        return expression_tree.postfix, dfa, minimized_dfa

regular_expression =''
while regular_expression != 'salir':
    regular_expression = input("Ingrese una expresión regular valida: ")
    if regular_expression != 'salir':
        postfix, dfa, minimized_dfa = thompson_algorithm(regular_expression)
        print(''.join(postfix))
        postfixaumentado = ''.join(postfix)
        postfixaumentado += '#'
        print(postfixaumentado)
    else:
        print('Saliste del compilador, Gracias')
