from collections import deque
from AFN import *
from keys import *
from Node import Node

class AFD:
    def __init__(self, symbols):
        self.nfa = None
        self.tree = None
        self.states = None
        self.state_id_mapping = {}
        self.symbols = symbols
        self.transitions = {}
        self.initial = None
        self.final = None
        self.state_count = 0

    # /-------------------------------NFA to DFA por subconjuntos-------------------------------/
    # /-------------------------------NFA to DFA por subconjuntos-------------------------------/
    # /-------------------------------NFA to DFA por subconjuntos-------------------------------/
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

    # /-------------------------------postfix to DFA-------------------------------/
    # /-------------------------------postfix to DFA-------------------------------/
    # /-------------------------------postfix to DFA-------------------------------/
    def get_next_state(self, state_set, symbol):
        next_positions = set()
        for position in state_set:
            if self.tree.search_by_id(position) == symbol:
                next_positions |= set(self.tree.nextpos[position])
        return next_positions

    def generate_state_id(self):
        state_id = self.state_count
        self.state_count += 1
        return state_id

    def directBuild(self, tree):
        self.tree = tree
        start_state = frozenset(self.tree.firstpos[self.tree.tree.id])
        self.initial = start_state
        unmarked_states = [start_state]
        self.states = {start_state}
        self.state_id_mapping[start_state] = self.generate_state_id()
        while unmarked_states:
            current_state = unmarked_states.pop()
            for symbol in self.tree.symbols:
                next_state = frozenset(self.get_next_state(current_state, symbol))
                if next_state:
                    if next_state not in self.states:
                        unmarked_states.append(next_state)
                        self.states.add(next_state)
                        self.state_id_mapping[next_state] = self.generate_state_id()
                    if current_state not in self.transitions:
                        self.transitions[current_state] = {}
                    self.transitions[current_state][symbol] = next_state
        self.final = {state for state in self.states if self.tree.tree.id in state}

    # /-------------------------------Minimizacion de DFA-------------------------------/
    # /-------------------------------Minimizacion de DFA-------------------------------/
    # /-------------------------------Minimizacion de DFA-------------------------------/
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

    # /-------------------------------Funcion para mostrar AFD-------------------------------/
    # /-------------------------------Funcion para mostrar AFD-------------------------------/
    # /-------------------------------Funcion para mostrar AFD-------------------------------/
    def printDFA(self):
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

    def showDFA(self):
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

    # /-------------------------------Simulacion del AFD-------------------------------/
    # /-------------------------------Simulacion del AFD-------------------------------/
    # /-------------------------------Simulacion del AFD-------------------------------/
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
