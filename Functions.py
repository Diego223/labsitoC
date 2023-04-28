#***************************************************************************
def is_empty(stack):
    return len(stack) == 0

def last(stack):
    return stack[-1]

def pop(stack):
    if not is_empty(stack):
        return stack.pop()
    else:
        BaseException("Error")

def push(stack, op):
    stack.append(op)

#***************************************************************************
def replace_reserved_words(r: str):
    return (r
            .replace('(', 'Þ')
            .replace(')', 'δ')
            .replace('{', 'ζ')
            .replace('}', 'η')
            .replace('[', 'θ')
            .replace(']', 'ω')
            .replace('|', '¶')
            .replace('+', 'µ')
            .replace('-', 'ß')
            )
    
def return_reserved_words(r: str):
    return (r
            .replace('Þ', '(')
            .replace('δ', ')')
            .replace('ζ', '{')
            .replace('η', '}')
            .replace('θ', '[')
            .replace('ω', ']')
            .replace('¶', '|')
            .replace('µ', '+')
            .replace('ß', '-')
            )

def process_string(s: str):
    result = []
    in_quotes = False
    start_idx = 0
    for i, char in enumerate(s):
        if char == '"':
            if in_quotes:
                # End of quoted substring; apply replace_reserved_words
                result.append(replace_reserved_words(s[start_idx:i]))
                in_quotes = False
            else:
                # Copy unprocessed substring and start of quoted substring
                result.append(s[start_idx:i])
                in_quotes = True
            start_idx = i + 1
    result.append(s[start_idx:])
    return ''.join(result)

def process_string(s: str):
    result = []
    in_quotes = False
    start_idx = 0
    for i, char in enumerate(s):
        if char == "'":
            if in_quotes:
                # End of quoted substring; apply replace_reserved_words
                result.append(replace_reserved_words(s[start_idx:i]))
                in_quotes = False
            else:
                # Copy unprocessed substring and start of quoted substring
                result.append(s[start_idx:i])
                in_quotes = True
            start_idx = i + 1
        #if char is \ and next char is s, replace with space
        elif char == "\\":
            if s[i+1] == "s":
                result.append(s[start_idx:i])
                result.append(" ")
                start_idx = i + 2
    # Append remaining unprocessed substring
    result.append(s[start_idx:])
    return ''.join(result)