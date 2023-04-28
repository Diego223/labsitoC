from keys import *
from scannerFunctions import *

class YalProcessor:
    def __init__(self, yal_file):
        self.yal_file = yal_file
        self.lines = []
        self.rules = {}
        self.comments = []
        self.ruleTokens = {}
        self.tokenRules = []
        self.tokensExp = ''
        self.process_yal()
        self.get_tokens()
        self.gen_file()

    @staticmethod
    def extract_rule(line):
        tokens = line.split('=')
        rule_name = tokens[0].strip()[4:]
        rule_body = tokens[1].strip()
        return rule_name, rule_body

    @staticmethod
    def convert_to_regex(rule_body):
        regex_rule = ""
        i = 0
        while i < len(rule_body):
            if rule_body[i] == Lbrace:
                i += 1
                inside_brackets = ""
                while rule_body[i] != Rbrace:
                    inside_brackets += rule_body[i]
                    i += 1
                ranges = inside_brackets.split("''")
                operands = []  # Initialize an empty list to store operands
                for r in ranges:
                    if '-' in r and r.index('-') > 0 and r.index('-') < len(r) - 1:
                        start, end = r.split('-')
                        start = start.replace("'", "")  # Remove single quotes from start
                        end = end.replace("'", "")  # Remove single quotes from end
                        string = start + '-' + end   # Create a range string
                        operands.append(string)  # Add the range to the operands list
                    else:
                        r = r.replace("'", "")  # Remove single quotes from r
                        for x in r:
                            if x in [*operators, minus]:
                                r = f"'{x}'" 
                        operands.append(r)  # Add the character to the operands list 
                #join operands with l paren and right paren when they dont have 
                regex_rule += Lparen + alternative.join(operands ) + Rparen
            else:
                regex_rule += rule_body[i]
            i += 1
        return regex_rule


    #Metodo de lectura y apertura del archivo.
    def extract_lines(self):
        with open(self.yal_file, 'r') as f:
            lines = f.readlines()
        self.lines = lines

    #Extraccion de comentarios
    def extract_comments(self):
            #Recorremos las lineas
        for line in self.lines:
            #Buscamos si inicia con lo siguiente sintaxis de comentarios , si si, se va a comentarios.
            if startsWith(line, "'('*") and endsWith(line, "*')'"):
                self.comments.append(line)
            else: 
                regex = "'('* (A-Z)(a-z)+ ((a-z)+((, )| ))∗*')'"
                finds = findIn(line, regex)
                if len(finds)>0 and finds[0] not in self.comments:
                    self.comments.append(finds[0])


    def process_yal(self):
        self.extract_lines()
        self.extract_comments()
        for line in self.lines:
            if startsWith(line, "let"):
                line = line.replace('*', '∗')
                line = line.replace('"', "'")

                rule_name, rule_body = self.extract_rule(line)
                regex_rule = self.convert_to_regex(rule_body)
                self.rules[rule_name] = regex_rule
        # Replace rules in other rules
        for rule_name, regex_rule in self.rules.items():
            updated_rule = self.replace_rules(regex_rule)
            self.rules[rule_name] = updated_rule

    #Metodo para ordenar las reglas, recibimos expresion regular, ordenamos y verificamos las reglas.
    def replace_rules(self, regex_rule):
        sorted_rule_names = sorted(self.rules.keys(), key=len, reverse=True)
        for rule_name in sorted_rule_names:
            rule_body = self.rules[rule_name]
            if rule_name in regex_rule:
                if regex_rule.endswith(f"{rule_name}+") or (f"{rule_name}+" in regex_rule):
                    if rule_body.startswith(Lparen) and rule_body.endswith(Rparen):
                        regex_rule = regex_rule.replace(f"{rule_name}+", f'{rule_body}+')
                    else:
                        regex_rule = regex_rule.replace(f"{rule_name}+", f'({rule_body})+')
                else:
                    regex_rule = regex_rule.replace(rule_name, f'{rule_body}')
        return regex_rule


    #Extraemos los tokens y reglas del .yal y los organizamos para generar el file.
    def get_tokens(self):
        rulelines = [] # lista vacía para almacenar las líneas de las reglas
        returns = {} # diccionario vacío para almacenar los valores de retorno de las reglas
        
        # Obtener solo las líneas desde "rule tokens" hasta el final
        for i in range(len(self.lines)):
            if startsWith(self.lines[i], "rule tokens"):
                rulelines = self.lines[i+1:-2]
                break
                
        # Primero, verificar las líneas que no tienen un valor de retorno
        norets = findMissing(rulelines, "'{' return (A-Z)+ '}'")
        for key, value in norets.items():
            value = 'NS' # si no hay un valor de retorno, se le asigna el valor 'NS' (no especificado)
            returns[key] = value # se almacena el valor de retorno en el diccionario 'returns'
        
        # Obtener los tokens y sus expresiones
        for line in rulelines:
            line = splitString(line, " ") # separar cada línea por espacios en blanco
            line = [x for x in line if x != ''] # eliminar las cadenas vacías en la línea
            if not matches(line[0], "'|'"): # verificar si la línea no comienza con el carácter '|'
                if line[0][-1] == "\n": # verificar si la línea termina con un salto de línea
                    line[0] = line[0][:-1] # si es así, eliminar el salto de línea de la cadena
                line = [line[0]] # agregar la cadena a una lista
                if len(line) == 1:
                    returns[0] = 'NS'
            else:
                line = line[:2]
                if '"' in line[1]:
                    line[1] = line[1].replace('"', "'")
            
            if len(line) > 1:
                self.tokenRules.append(line[1]) # si la línea tiene más de una cadena, la segunda cadena es la expresión del token
            elif len(line) == 1:
                self.tokenRules.append(line[0]) # si la línea solo tiene una cadena, esta es la expresión del token
            self.tokensExp += ''.join(line) # se agrega la cadena a la expresión de tokens
            
        self.tokensExp = self.replace_rules(self.tokensExp) # se reemplazan las reglas en la expresión de tokens
        
        # Obtener qué valor retorna cada regla
        returns.update(findAll(rulelines, "'{' return (A-Z)+ '}'"))
        for key, value in returns.items():
            value = splitString(value[0][0])
            for x in value:
                if matches(x, '(A-Z)+'):
                    returns[key] = x
                    
        for i in range(len(self.tokenRules)):
            self.ruleTokens[self.replace_rules(self.tokenRules[i])] = returns[i] # almacenar cada regla y su valor de retorno en un diccionario 'ruleTokens'




    def gen_file(self):
        content = ''
        content += "\
from keys import *\n\
from scannerFunctions import *\n\
from AFD import *\n\
from ExpressionTree import *\n\
from regularExpression import *\n\
\n\
"       '#Generacion de reglas para el scanner \n' 
        #Agregamos el contenido de las reglas
        for key, value in self.rules.items():
            content+= f'{key} = "{value}"\n'
        content += "\n"
        content += f'\
rules = {self.ruleTokens}\n\
\n\
rulexpressions = "{self.tokensExp}"\n\
#Generacion de expresion regular aumentada utilizando las reglas \n\
tokensRegex = regularExpression(rulexpressions)\n\
tokensRegex.augmentRegex()\n\
#Generacion de arbol utilizando expresion aumentada a postfix \n\
tokenTree = ExpressionTree(tokensRegex.postfix)\n\
tokenTree.showTable()\n\
dfa = AFD(tree = tokenTree)\n\
#Generacion de AFD directo \n\
showDirect(dfa, "Directo DFA")\n\
lineas = []\n\
#Lectura de archivo a correr \n\
archivo = input("Ingrese el numero de archivo yal.run (1.1 | 1.2): ") \n\
archivo = "slr-" + archivo + ".yal.run"\n\
#Escaneamos archivo buscando tokens que coincidan con las reglas definidas.\n\
with open(archivo, "r") as f:\n\
    lineas = f.readlines()\n\
\
finds = findAll(lineas, rulexpressions)\n\
llaves = []\n\
for key, value in finds.items():\n\
    for y in rules.keys():\n\
        for i in range(len(value)):\n\
            if matches(value[i][0], y):\n\
                llaves.append([key, value[i][0], rules[y], value[i][1], value[i][2]])\n\
\n\
#Printeamos resultados\n\
print("\\n\\n Llaves Encontradas\\n")\n\
for x in llaves:\n\
    print(x[2], " encontrado en la linea ", x[0])\n\
    print("La llave es: ", x[1])\n\
    print("Inicia en: ", x[3])\n\
    print("Finaliza en: ", x[4], "\\n\\n")\n\
'
        #Generacion de archivo python
        with open(f"scanner.py", "w", encoding='UTF-8') as f:
            f.write(content)
