from keys import *

class YalProcessor:
    def __init__(self, yal_file):
        self.yal_file = yal_file
        self.rules = {}
        self.process_yal()

    def process_yal(self):
        with open(self.yal_file, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line.startswith("let"):
                    rule_name, rule_body = self.extract_rule(line)
                    regex_rule = self.convert_to_regex(rule_body)
                    self.rules[rule_name] = regex_rule

            # Replace rules in other rules
            for rule_name in sorted(self.rules.keys(), key=len, reverse=True):
                rule_body = self.rules[rule_name]
                for sub_rule_name in self.rules.keys():
                    if sub_rule_name in rule_body:
                        sub_rule_body = self.rules[sub_rule_name]
                        if rule_body.endswith(f"{sub_rule_name}†") or (f"{sub_rule_name}†" in rule_body):
                            if sub_rule_body.startswith(Lparen) and sub_rule_body.endswith(Rparen):
                                rule_body = rule_body.replace(f"{sub_rule_name}†", f'{sub_rule_body}†')
                            else:
                                rule_body = rule_body.replace(f"{sub_rule_name}†", f'({sub_rule_body})†')
                        else:
                            rule_body = rule_body.replace(sub_rule_name, f'{sub_rule_body}')
                self.rules[rule_name] = rule_body

    @staticmethod
    def extract_rule(line):
        rule_name, rule_body = line.split('=', maxsplit=1)
        return rule_name.strip()[4:], rule_body.strip()

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
                        for char_code in range(ord(start), ord(end) + 1):
                            operands.append(chr(char_code))  # Add the character to the operands list
                    else:
                        r = r.replace("'", "")  # Remove single quotes from r
                        operands.append(r)  # Add the character to the operands list
                regex_rule += Lparen + alternative.join(operands) + Rparen  # Join the operands using alternative and surround them with parentheses
            else:
                regex_rule += rule_body[i]
            i += 1
        return regex_rule.replace("'", "")
