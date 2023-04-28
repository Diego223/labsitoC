from Functions import *
from regularExpression import *
from ExpressionTree import *
from AFD import *

def matches(string, regex):
    regex = regularExpression(regex)
    regex.augmentRegex()
    # print("postfix expression", return_reserved_words(''.join(regex.postfix)))
    tree = ExpressionTree(regex.postfix)
    dfa = AFD(tree = tree)
    return dfa.simulate(string)

def splitString(string, delimiter=' '):
    result = []
    current_word = ''
    delimiter_length = len(delimiter)
    index = 0
    while index < len(string):
        if string[index:index + delimiter_length] == delimiter:
            result.append(current_word)
            current_word = ''
            index += delimiter_length  
        else:
            current_word += str(string[index])
            index += 1
    result.append(current_word)
    return result

def startsWith(line, prefix, delimiter=None):
    if delimiter == None:
        prefix_words = splitString(prefix)
        prefix_length = len(prefix_words)
        string_words = splitString(line)
        string_length = len(string_words)
    else:
        prefix_words = splitString(prefix, delimiter)
        prefix_length = len(prefix_words)
        string_words = splitString(line, delimiter)
        string_length = len(string_words)
    if prefix_length == 1:
        if matches(string_words[0], prefix):
            return True
        else:
            return False
    else:
        string_words = splitString(line)
        if string_length < prefix_length:
            return False
        else:
            for i in range(prefix_length):
                if not matches(string_words[i], prefix_words[i]):
                    return False
            return True

def endsWith(string, suffix, delimiter=None):
    if not delimiter:
        suffix_words = splitString(suffix)
        suffix_length = len(suffix_words)
        string_words = splitString(string)
        string_length = len(string_words)
    else:
        suffix_words = splitString(suffix, delimiter)
        suffix_length = len(suffix_words)
        string_words = splitString(string, delimiter)
        string_length = len(string_words)
    if suffix_length == 1:
        if matches(string_words[-1], suffix):
            return True
        else:
            return False
    else:
        string_words = splitString(string)
        if string_length < suffix_length:
            return False
        else:
            for i in range(suffix_length):
                if not (string_words[-(i + 1)], suffix_words[-(i + 1)]):
                    return False
            return True

def findIn(line, regex):
    regex = regularExpression(regex)
    regex.augmentRegex()
    # print("postfix expression", return_reserved_words(''.join(regex.postfix)))
    tree = ExpressionTree(regex.postfix)
    dfa = AFD(tree = tree)
    return dfa.scanner(line)

def findAll(lines, regex):
    finds = {}
    for i in range(len(lines)):
        find = findIn(lines[i], regex)
        if len(find) > 0:
            finds[i] = find
        else:
            continue
    return finds

def findMissing(lines, regex):
    finds = {}
    for i in range(len(lines)):
        find = findIn(lines[i], regex)
        if len(find) > 0:
            finds[i] = find[0]
        else:
            continue
    return finds
