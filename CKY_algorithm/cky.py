"""
COMS W4705 - Natural Language Processing
Homework 2 - Parsing with Context Free Grammars 
Yassine Benajiba
"""
import math
import sys
from collections import defaultdict
import itertools
from grammar import Pcfg

### Use the following two functions to check the format of your data structures in part 3 ###
def check_table_format(table):
    """
    Return true if the backpointer table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Backpointer table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and \
          isinstance(split[0], int)  and isinstance(split[1], int):
            sys.stderr.write("Keys of the backpointer table must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of backpointer table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            bps = table[split][nt]
            if isinstance(bps, str): # Leaf nodes may be strings
                continue 
            if not isinstance(bps, tuple):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Incorrect type: {}\n".format(bps))
                return False
            if len(bps) != 2:
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Found more than two backpointers: {}\n".format(bps))
                return False
            for bp in bps: 
                if not isinstance(bp, tuple) or len(bp)!=3:
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has length != 3.\n".format(bp))
                    return False
                if not (isinstance(bp[0], str) and isinstance(bp[1], int) and isinstance(bp[2], int)):
                    print(bp)
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has incorrect type.\n".format(bp))
                    return False
    return True

def check_probs_format(table):
    """
    Return true if the probability table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Probability table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and isinstance(split[0], int) and isinstance(split[1], int):
            sys.stderr.write("Keys of the probability must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of probability table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            prob = table[split][nt]
            if not isinstance(prob, float):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a float.{}\n".format(prob))
                return False
            if prob > 0:
                sys.stderr.write("Log probability may not be > 0.  {}\n".format(prob))
                return False
    return True



class CkyParser(object):
    """
    A CKY parser.
    """

    def __init__(self, grammar): 
        """
        Initialize a new parser instance from a grammar. 
        """
        self.grammar = grammar

    def is_in_language(self,tokens):
        """
        Membership checking. Parse the input tokens and return True if 
        the sentence is in the language described by the grammar. Otherwise
        return False
        """
        # TODO, part 2

        #table, probs = self.parse_with_backpointers(tokens)
        #if grammar.startsymbol in table[(0, len(tokens))]:
        #    return True
        
        #return False 
        table = {}
        rhs_rules = self.grammar.rhs_to_rules

        for i in range(0, len(tokens)+1):
            for j in range(i+1, len(tokens)+1):
                table[(i,j)] = {}
    
        
        #fill parse table of span 1
        for i in range(0, len(tokens)):
            rules = rhs_rules[(tokens[i],)]
            for r in rules:
                nonterminal = r[0]
                table[(i,i+1)][nonterminal] = ()   
        
        for l in range(2, len(tokens)+1):
            for i in range(0, len(tokens)+1-l):
                j = i + l    

                for k in range(i+1, j):
                    nont_1 = table[(i,k)]
                    nont_2 = table[(k,j)]  

                    for nonterminal1 in nont_1:
                        for nonterminal2 in nont_2:
                            nonterminal_p = (nonterminal1, nonterminal2)

                            if nonterminal_p in rhs_rules:
                                r_rules = rhs_rules[nonterminal_p]

                                for r in r_rules:
                                    new_nonterminal = r[0]
                                    table[(i,j)][new_nonterminal] = ()
        
        if grammar.startsymbol in table[(0, len(tokens))]:
            return True
        
        return False 


    def parse_with_backpointers(self, tokens):
        """
        Parse the input tokens and return a parse table and a probability table.
        """
        # TODO, part 3
        table = {}
        probs = {}
        rhs_rules = self.grammar.rhs_to_rules

        for i in range(0, len(tokens)+1):
            for j in range(i+1, len(tokens)+1):
                table[(i,j)] = {}
                probs[(i,j)] = {}
        
        #fill parse table of span 1
        for i in range(0, len(tokens)):
            rules = rhs_rules[(tokens[i],)]

            for r in rules:
                nonterminal = r[0]
                prob_rule = math.log2(r[2])
                table[(i,i+1)][nonterminal] = tokens[i]
                probs[(i,i+1)][nonterminal] = prob_rule

        # parse table of different length 2 and more
        for length in range(2, len(tokens)+1):
            # search all possibilities of span of current length
            for i in range(0, len(tokens)+1-length):
                j = i + length

                #every combinations of i+1 to j with different k
                for k in range(i+1, j):
                    #nonterminals for these combinations
                    nont_1 = table[(i,k)]
                    nont_2 = table[(k,j)]
                    
                    for nonterminal1 in nont_1:
                        for nonterminal2 in nont_2:
                            nonterminal_p = (nonterminal1, nonterminal2)

                            # check if obeys the rule
                            if nonterminal_p in rhs_rules:
                                r_rules = rhs_rules[nonterminal_p]

                                # reserve new nonterminal
                                for r in r_rules:
                                    new_nonterminal = r[0]

                                    prob_s_1 = probs[(i,k)][nonterminal1]
                                    # according to prob of span 1, this is already the form of log
                                    prob_s_2 = probs[(k,j)][nonterminal2]
                                    new_prob_rule = math.log2(r[2])
                                    new_prob = prob_s_1 + prob_s_2 + new_prob_rule

                                    backpointer1 = (nonterminal_p[0],i,k)
                                    backpointer2 = (nonterminal_p[1],k,j)

                                    if new_nonterminal not in table[(i,j,)]:
                                        table[(i,j)][new_nonterminal] = (backpointer1, backpointer2)
                                        probs[(i,j)][new_nonterminal] = new_prob
                                    else:
                                        if new_prob > probs[(i,j)][new_nonterminal]:
                                            table[(i,j)][new_nonterminal] = (backpointer1, backpointer2)
                                            probs[(i,j)][new_nonterminal] = new_prob

        return table, probs


def get_tree(chart, i,j,nt):
    """
    Return the parse-tree rooted in non-terminal nt and covering span i,j.
    """
    
    # TODO: Part 4 
    if isinstance(chart[(i,j)][nt], str):
        return (nt, chart[(i,j)][nt])
    else:
        #get backpointer
        l_backpointer = chart[(i,j)][nt][0]
        r_backpointer = chart[(i,j)][nt][1]

        # Finally, recurse over left and right child
        # Don't forget to add current parse result nt
        return (nt, get_tree(chart, l_backpointer[1], l_backpointer[2], l_backpointer[0]), get_tree(chart, r_backpointer[1], r_backpointer[2], r_backpointer[0]))

 
       
if __name__ == "__main__":
    
    with open('atis3.pcfg','r') as grammar_file: 
        grammar = Pcfg(grammar_file) 
        parser = CkyParser(grammar)
        toks =['flights', 'from','miami', 'to', 'cleveland','.'] 
        print(parser.is_in_language(toks))
        table,probs = parser.parse_with_backpointers(toks)
        print(check_table_format(table))
        print(check_probs_format(probs))
        print(get_tree(table, 0, len(toks), grammar.startsymbol))
   
        
