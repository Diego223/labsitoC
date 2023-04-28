from keys import *
from scannerFunctions import *
from AFD import *
from ExpressionTree import *
from regularExpression import *

#Generacion de reglas para el scanner 
delim = "( |\t|\n)"
ws = "( |\t|\n)+"
letter = "(A-Z|a-z)"
digit = "(0-9)"
id = "(A-Z|a-z)((A-Z|a-z)|(0-9))∗"

rules = {'( |\\t|\\n)+': 'N', '(A-Z|a-z)((A-Z|a-z)|(0-9))∗': 'ID', "'+'": 'PLUS', "'*'": 'TIMES', "'('": 'LPAREN', "')'": 'RPAREN'}

rulexpressions = "( |\t|\n)+|(A-Z|a-z)((A-Z|a-z)|(0-9))∗|'+'|'*'|'('|')'"
#Generacion de expresion regular aumentada utilizando las reglas 
tokensRegex = regularExpression(rulexpressions)
tokensRegex.augmentRegex()
#Generacion de arbol utilizando expresion aumentada a postfix 
tokenTree = ExpressionTree(tokensRegex.postfix)
tokenTree.showTable()
dfa = AFD(tree = tokenTree)
#Generacion de AFD directo 
showDirect(dfa, "Directo DFA")
lineas = []
#Lectura de archivo a correr 
archivo = input("Ingrese el numero de archivo yal.run (1.1 | 1.2):") 
archivo = "slr-" + archivo + ".yal.run"
#Escaneamos archivo buscando tokens que coincidan con las reglas definidas.
with open(archivo, "r") as f:
    lineas = f.readlines()
finds = findAll(lineas, rulexpressions)
llaves = []
for key, value in finds.items():
    for y in rules.keys():
        for i in range(len(value)):
            if matches(value[i][0], y):
                llaves.append([key, value[i][0], rules[y], value[i][1], value[i][2]])

#Printeamos resultados
print("\n\n Llaves Encontradas\n")
for x in llaves:
    print(x[2], " encontrado en la linea ", x[0])
    print("La llave es: ", x[1])
    print("Inicia en: ", x[3])
    print("Finaliza en: ", x[4], "\n\n")
