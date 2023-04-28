from regularExpression import regularExpression
from ExpressionTree import ExpressionTree
from Functions import *
from AFN import AFN
from AFD import *
from AFD import AFD
import functools
import timeit

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
    regular_expression = regularExpression(regular_expression)
    regular_expression.augmentRegex()
    postfix_expression = regular_expression.postfix
    expression_tree = ExpressionTree(postfix_expression)
    expression_tree.showTable()
    #NFA GENERATION
    # nfa = AFN()
    # nfa.generate_AFN_from_re(regularExpression)
    # print(nfa)
    # nfa.graph_AFN()

    # #NFA TO DFA ALGORITHM
    # dfa = AFD(nfa)  
    # print(dfa)
    # dfa.nfa_to_dfa() 
    # dfa.showDFA()
    # # Apply DFA minimization
    # dfa.minimize()
    # dfa.showDFA()

    #DIRECT DFA 
    dfa = AFD(tree=expression_tree)
    # Simulacion
    opcion =''
    while opcion != '1' and opcion !='2':    
        opcion = input('\n 1. Simular DFA Directo \n 2. Simular NFA \n opcion: ')    
        if (opcion =='1'):
            Verificador = ""
            while Verificador != 'salir':
                Verificador = input("\nIngrese la cadena a revisar o escriba 'salir' ")
                if Verificador != 'salir':
                    result = dfa.simulate_direct(Verificador)
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

def testSimulation(regular_expression: str, Verificador: str):
    regex = regularExpression(regular_expression)
    regex.augmentRegex()
    print("postfix expression", return_reserved_words(''.join(regex.postfix)))
    tree = ExpressionTree(regex.postfix)
    dfa = AFD(tree=tree)
    return dfa.simulate(Verificador)

regular_expression =''
while regular_expression != 'salir':
    regular_expression = input("Ingrese una expresión regular valida: ")
    if regular_expression != 'salir':
        Verificador = input("Ingrese la cadena a revisar: ")
        result = testSimulation(regular_expression, Verificador)
        print(result)
        # postfix, dfa, minimized_dfa = thompson_algorithm(regular_expression)
        
    else:
        print('Saliste del compilador, Gracias')
