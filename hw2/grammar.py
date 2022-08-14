"""
COMS W4705 - Natural Language Processing
Homework 2 - Parsing with Context Free Grammars 
Yassine Benajiba
"""

from pickle import TRUE
import sys
from collections import defaultdict
from math import fsum

class Pcfg(object): 
    """
    Represent a probabilistic context free grammar. 
    """

    def __init__(self, grammar_file): 
        self.rhs_to_rules = defaultdict(list)
        self.lhs_to_rules = defaultdict(list)
        self.startsymbol = None 
        self.read_rules(grammar_file)      
 
    def read_rules(self,grammar_file):
        
        for line in grammar_file: 
            line = line.strip()
            if line and not line.startswith("#"):
                if "->" in line: 
                    rule = self.parse_rule(line.strip())
                    lhs, rhs, prob = rule
                    self.rhs_to_rules[rhs].append(rule)
                    self.lhs_to_rules[lhs].append(rule)
                else: 
                    startsymbol, prob = line.rsplit(";")
                    self.startsymbol = startsymbol.strip()
                    
     
    def parse_rule(self,rule_s):
        lhs, other = rule_s.split("->")
        lhs = lhs.strip()
        rhs_s, prob_s = other.rsplit(";",1) 
        prob = float(prob_s)
        rhs = tuple(rhs_s.strip().split())
        return (lhs, rhs, prob)

    def verify_grammar(self):
        """
        Return True if the grammar is a valid PCFG in CNF.
        Otherwise return False. 
        """
        # TODO, Part 1
        # All nonterminal symbols are upper-case
        # have 2 nonterminal symbols or 1 terminal
        # lhs symbol sum up to 1
        for nonterminal in self.lhs_to_rules:
            if self.is_nonterminal_valid(nonterminal):
                return True
            else:
                print('The nonterminal does not follow the format:', nonterminal)

            if self.production_rule_prob(self.lhs_to_rules[nonterminal]):
                return True
            else:
                print('The nonterminal production rule probabilities does not sum up to 1:', nonterminal)
        
        return False
            

    def is_nonterminal_valid(self, nonterminal):
        return nonterminal.isupper()
    
    def production_rule_prob(self, triples):
        total_prob = float(0.0)
        probs = ()
        for i in triples:
            probs.append(i[2])
        total_prob = fsum(probs)
        if total_prob != float(1.0):
            print('The production rule probabilities for the nonterminal do not equals to 1:', str(triples[0][0]))
            print(total_prob)
            return False
        
        return True
            


if __name__ == "__main__":
    with open('atis3.pcfg','r') as grammar_file:
        grammar = Pcfg(grammar_file)
        print(grammar.startsymbol)
    if grammar.verify_grammar():
        print('THE GRAMMAR IS A VALID PCFG IN CNF')
    else:
        sys.stderr.write('THE GRAMMAR IS NOT VALID')
        
