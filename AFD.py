from collections import deque
from Functions import *
from AFN import *
from keys import *
from Node import Node
import graphviz

class AFD:
    def __init__(self, symbols=None, tree:ExpressionTree = None, nfa:AFN = None):
        if tree != None:
            self.tree =tree
            self.nullable = self.tree.nullable
            self.firstpos = self.tree.firstpos
            self.lastpos = self.tree.lastpos
            self.nextpos = self.tree.nextpos
            self.nodes = self.tree.nodes
            self.symbols = self.tree.symbols
            self.states = []
            self.transition_table = {}
            self.final_states = set()
            self.build_dfa()
        if nfa != None and symbols != None:
            self.nfa = nfa
            self.states = None
            self.state_id_mapping = {}
            self.symbols = symbols
            self.transitions = {}
            self.initial = None
            self.final = None
            self.state_count = 0

#***************************************************************************
    def e_closure(self, states):
        closure = set(states)
        stack = list(states)
        while stack:
            current_state = stack.pop()
            if (current_state, epsilon) in self.nfa.transitions:
                next_states = set(
                    self.nfa.transitions[(current_state, epsilon)])
                new_states = next_states - closure
                stack.extend(new_states)
                closure |= next_states
        return closure
    
    def move(self, state_set, symbol):
        moves = set()
        for state in state_set:
            if (state, symbol) in self.nfa.transitions:
                moves |= set(self.nfa.transitions[(state, symbol)])
        return moves
    
    def subsets(self, nfa: AFN):
        self.nfa = nfa
        self.state_id_mapping = {}
        self.next_state_id = 1
        dfa_states = []
        dfa_transitions = {}
        queue = deque([self.e_closure({self.nfa.initial})])
        while queue:
            current_state_set = queue.popleft()
            dfa_states.append(frozenset(current_state_set))
            self.state_id_mapping[frozenset(current_state_set)] = self.next_state_id
            self.next_state_id += 1
            for symbol in self.nfa.symbols:
                if symbol == epsilon:
                    continue
                move_result = self.move(current_state_set, symbol)
                target_state_set = self.e_closure(move_result)
                if len(target_state_set) > 0:
                    target_state_set = frozenset(target_state_set)
                    if target_state_set not in dfa_states:
                        queue.append(target_state_set)
                    if frozenset(current_state_set) not in dfa_transitions:
                        dfa_transitions[frozenset(current_state_set)] = {}
                    dfa_transitions[frozenset(current_state_set)][symbol] = target_state_set
        self.states = dfa_states
        self.transitions = dfa_transitions
        self.initial = frozenset(self.e_closure({self.nfa.initial}))
        self.final = [state_set for state_set in dfa_states if self.nfa.final in state_set]


#***************************************************************************
    def closure(self, positions):
        result = set(positions)
        for pos in positions:
            if self.nodes[pos] == epsilon:
                result |= self.closure(self.nextpos[pos])
        return result

    def build_dfa(self):
        initial_state = frozenset(self.closure(self.firstpos[self.tree.tree.id]))
        unmarked_states = [initial_state]
        self.states.append(initial_state)
        self.transition_table[initial_state] = {}
        while unmarked_states:
            current_state = unmarked_states.pop()
            for symbol in self.symbols:
                next_positions = set()
                for pos in current_state:
                    if self.nodes[pos] == symbol:
                        next_positions |= set(self.nextpos[pos])  # Convert list to set before union operation
                next_positions_closure = frozenset(self.closure(next_positions))
                if not next_positions_closure:
                    continue
                if next_positions_closure not in self.states:
                    self.states.append(next_positions_closure)
                    unmarked_states.append(next_positions_closure)
                    self.transition_table[next_positions_closure] = {}
                self.transition_table[current_state][symbol] = next_positions_closure
        hash_position = self.tree.tree.right.id
        for state in self.states:
            if hash_position in state:
                self.final_states.add(state)

    def simulate(self, input_string):
        input_string = replace_reserved_words(input_string)
        current_state = self.states[0]
        for symbol in input_string:
            if symbol not in self.symbols:
                return False
            next_state = self.transition_table[current_state].get(symbol)
            if not next_state:
                return False
            current_state = next_state
        return current_state in self.final_states

#***************************************************************************
    def minimize(self):
        part = [item for item in self.states if item not in self.final]
        partitions = [part, self.final]
        added = True
        while added:
            added = False
            for i in partitions:
                if len(i) > 1:
                    for s in self.nfa.symbols:
                        new_part = []
                        target = -1
                        for j in i:
                            result = self.move(j, s)
                            if len(result) > 0:
                                for part in partitions:
                                    if result in part:
                                        if target == -1 or target == partitions.index(part):
                                            target = partitions.index(part)
                                        else:
                                            new_part.append(j)
                        if len(new_part) > 0:
                            for part in partitions:
                                partitions[partitions.index(part)] = list(set(part) - set(new_part))
                            partitions.append(new_part)
                            added = True
        for part in partitions:
            removed = []
            for state in part:
                if part.index(state) > 0:
                    self.states.remove(state)
                    if state in self.initial:
                        self.initial.remove(state)
                        self.initial.append(part[0])
                    if state in self.final:
                        self.final.remove(state)
                        self.final.append(part[0])
                for tran, targets in self.transitions.items():
                    for k in targets:
                        if k == state:
                            self.transitions[tran][k] = part[0]
        new_trans = {}
        for i, targets in self.transitions.items():
            if i not in new_trans:
                new_trans[i] = {}
            for symbol, target in targets.items():
                if symbol not in new_trans[i]:
                    new_trans[i][symbol] = target
        self.transitions = new_trans

    def simulate_subsets(self, input_string):
        current_state = frozenset(self.initial)
        for symbol in input_string:
            if symbol not in self.symbols:
                return False
            if current_state not in self.transitions or symbol not in self.transitions[current_state]:
                return False
            current_state = self.transitions[current_state][symbol]
        for final_state_set in self.final:
            if current_state.issubset(final_state_set):
                return True
        return False

    def simulate_direct(self, input_string):
        input_string = replace_reserved_words(input_string)
        current_state = self.states[0]
        for symbol in input_string:
            if symbol not in self.symbols:
                return False
            next_state = self.transition_table[current_state].get(symbol)
            if not next_state:
                return False
            current_state = next_state
        return current_state in self.final_states

    def scanner(self, input_string):
        input_string = replace_reserved_words(input_string)
        idx = 0
        results = []  # List to store all the matching substrings with their positions
        while idx < len(input_string):
            current_state = self.states[0]
            temp_idx = idx
            success = False
            matched_string = ""
            while temp_idx < len(input_string):
                symbol = input_string[temp_idx]
                if symbol not in self.symbols:
                    temp_idx += 1
                    continue
                next_state = self.transition_table[current_state].get(symbol)
                if not next_state:
                    break
                current_state = next_state
                temp_idx += 1
                if current_state in self.final_states:
                    success = True
                    matched_string = input_string[idx:temp_idx]
            if success:
                string = return_reserved_words(matched_string)
                results.append((string, idx, temp_idx - 1))  # Append the match and its positions to the results list
                idx = temp_idx  # Update the index to continue scanning from the next character
            else:
                idx += 1
        return results


#***************************************************************************
    def printSubsets(self):
        print("DFA Summary:")
        print("States:")
        for state_set in self.states:
            state_id = self.state_id_mapping[frozenset(state_set)]
            print(f"  State {state_id}: {state_set}")
        
        initial_state_id = self.state_id_mapping[frozenset(self.initial)]
        print(f"Initial State: {initial_state_id}")
        
        print("Final States:")
        for state_set in self.final:
            state_id = self.state_id_mapping[frozenset(state_set)]
            print(f"  State {state_id}")
        
        print("Transitions:")
        for state_set, transition in self.transitions.items():
            state_id = self.state_id_mapping[frozenset(state_set)]
            for symbol, target_state_set in transition.items():
                target_state_id = self.state_id_mapping[frozenset(target_state_set)]
                print(f"  {state_id} --({symbol})--> {target_state_id}")

    def showSubsets(self):
        with open('Graphs/AFD.dot', 'w', encoding='utf-8') as file:
            file.write('digraph{\n')
            file.write('rankdir=LR\n')
            file.write('node [shape=circle]\n')  # Add this line to set the default shape for nodes
            # Add this block to create subgraphs for non-final and final states
            file.write('{ rank=same; ')
            for state_set in self.states:
                state_name = str(self.state_id_mapping[frozenset(state_set)])
                if state_set != self.initial and state_set not in self.final:
                    file.write('"{}"; '.format(state_name))
            file.write('}\n')
            file.write('{ rank=max; ')
            for state_set in self.final:
                state_name = str(self.state_id_mapping[frozenset(state_set)])
                file.write('"{}"; '.format(state_name))
            file.write('}\n')
            for state_set in self.states:
                state_name = str(self.state_id_mapping[frozenset(state_set)])
                if state_set == self.initial:
                    file.write('"{}" [root=true]\n'.format(state_name))
                    file.write('fake [style=invisible]\n')
                    file.write(
                        'fake -> "{}" [style=bold]\n'.format(state_name))
                elif state_set in self.final:
                    file.write(
                        '"{}" [shape=doublecircle]\n'.format(state_name))
                else:
                    file.write('"{}"\n'.format(state_name))
            for state_set, transition in self.transitions.items():
                for symbol, target_state_set in transition.items():
                    file.write('"{}" -> "{}" [ label="{}" ]\n'.format(self.state_id_mapping[frozenset(
                        state_set)], self.state_id_mapping[frozenset(target_state_set)], symbol.replace('"', r'\"')))
            file.write('}\n')
        (graph,) = pydot.graph_from_dot_file('Graphs/AFD.dot')
        graph.write_png('Graphs/AFD.png')

    def print_direct(self):
        print("States:")
        for i, state in enumerate(self.states):
            print(f"State {i}: {state}")
        print("\nFinal States:")
        for state in self.final_states:
            print(state)
        print("\nTransition Table:")
        for state, transitions in self.transition_table.items():
            for symbol, next_state in transitions.items():
                print(f"{state} -- {symbol} --> {next_state}")

def showDirect(dfa: AFD, output_filename: str = 'DFADirect'):
    dot = graphviz.Digraph(format='dot', engine='dot')
    dot.graph_attr['rankdir'] = 'LR'
    dot.node_attr.update(shape='circle', fixedsize='true', width='1', height='1')

    start_state = dfa.states[0]
    dot.node(str(dfa.states.index(start_state)), label='', shape='none', width='0', height='0')
    dot.edge('', str(dfa.states.index(start_state)), label='', arrowhead='none')
    for final_state in dfa.final_states:
        dot.node(str(dfa.states.index(final_state)), peripheries='2')
    for state, transitions in dfa.transition_table.items():
        state_idx = dfa.states.index(state)
        for symbol, next_state in transitions.items():
            next_state_idx = dfa.states.index(next_state)
            dot.edge(str(state_idx), str(next_state_idx), label=symbol)
    dot.render(output_filename, view=False)
    dot.save(output_filename + '.dot')

#**************************************************AFD SIMULATION
    def simulate_dfa(self, input_string):
        current_state = frozenset(self.initial)
        for symbol in input_string:
            if symbol not in self.symbols:
                return False
            if current_state not in self.transitions or symbol not in self.transitions[current_state]:
                return False
            current_state = self.transitions[current_state][symbol]
        for final_state_set in self.final:
            if current_state.issubset(final_state_set):
                return True
        return False

    def simulate_direct(self, input_string):
            input_string = replace_reserved_words(input_string)
            current_state = self.states[0]
            for symbol in input_string:
                if symbol not in self.symbols:
                    return False
                next_state = self.transition_table[current_state].get(symbol)
                if not next_state:
                    return False
                current_state = next_state
            return current_state in self.final_states

    def scanner(self, input_string):
        input_string = replace_reserved_words(input_string)
        idx = 0
        while idx < len(input_string):
            current_state = self.states[0]
            temp_idx = idx
            success = False
            while temp_idx < len(input_string):
                symbol = input_string[temp_idx]
                if symbol not in self.symbols:
                    temp_idx += 1
                    continue
                next_state = self.transition_table[current_state].get(symbol)
                if not next_state:
                    break
                current_state = next_state
                temp_idx += 1
                if current_state in self.final_states:
                    success = True
                    break
            if success:
                string = return_reserved_words(input_string[idx:temp_idx])
                return string, idx, temp_idx - 1
            idx += 1
        return None, -1, -1
