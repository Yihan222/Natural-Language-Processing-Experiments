from conll_reader import DependencyStructure, DependencyEdge, conll_reader
from collections import defaultdict
import copy
import sys

import numpy as np
import keras

from extract_training_data import FeatureExtractor, State

class Parser(object): 

    def __init__(self, extractor, modelfile):
        self.model = keras.models.load_model(modelfile)
        self.extractor = extractor
        
        # The following dictionary from indices to output actions will be useful
        self.output_labels = dict([(index, action) for (action, index) in extractor.output_labels.items()])
    
    def sorted_prob(self, output):
        action_prob = []
        for i in range(0, len(output)):
            # use output_labels to map output to action
            action_prob.append((self.output_labels[i], output[i]))
            
        # use function sorted to descendingly sort prob
        sorted_action_prob = sorted(action_prob, key=lambda x:x[1],reverse=True)
        return sorted_action_prob
        
    
    def is_action_legal(self, action, state):
        # there are some transitions are not legal in some cases:

        lb = len(state.buffer)
        ls = len(state.stack)
        
        if action[0] == 'shift':
            if lb > 1: 
                return True
            elif lb == 1 and ls == 0: 
                return True
            else:
                return False
        
        elif action[0] == 'left_arc':
            if ls > 0:
                # not <'ROOT'>
                if state.stack[-1] != 0:
                    return True
            else:
                return False
        
        elif action[0] == 'right_arc':
            if ls > 0:
                return True
            else:
                return False


    def parse_sentence(self, words, pos):
        state = State(range(1,len(words)))
        state.stack.append(0)  

        count = 0  

        while state.buffer: 
            # 1. get input representation
            input = self.extractor.get_input_representation(words, pos, state)
            # input has to be reshaped
            input.reshape(1, -1)

            # 2. prediction
            output = self.model.predict(input.reshape(1, len(input)))
            # output is of size [1,91] it has to be converted to a list
            # which contains action and probability
            sorted_action_prob = self.sorted_prob(output[0])
            

            # to check whether it is legal for the action from the highest prob
            for i in range(0, len(sorted_action_prob)):
                action = sorted_action_prob[i][0]
                if self.is_action_legal(action, state):
                    if action[0] == 'shift':
                        state.shift()
                    elif action[0] == 'left_arc':
                        state.left_arc(action[1])
                    elif action[0] == 'right_arc':
                        state.right_arc(action[1])
                    break
            
            count += 1

        result = DependencyStructure()
        for p,c,r in state.deps: 
            result.add_deprel(DependencyEdge(c,words[c],pos[c],p, r))
        return result 
        

if __name__ == "__main__":

    WORD_VOCAB_FILE = 'data/words.vocab'
    POS_VOCAB_FILE = 'data/pos.vocab'

    try:
        word_vocab_f = open(WORD_VOCAB_FILE,'r')
        pos_vocab_f = open(POS_VOCAB_FILE,'r') 
    except FileNotFoundError:
        print("Could not find vocabulary files {} and {}".format(WORD_VOCAB_FILE, POS_VOCAB_FILE))
        sys.exit(1) 

    extractor = FeatureExtractor(word_vocab_f, pos_vocab_f)
    parser = Parser(extractor, sys.argv[1])

    with open(sys.argv[2],'r') as in_file: 
        for dtree in conll_reader(in_file):
            words = dtree.words()
            pos = dtree.pos()
            deps = parser.parse_sentence(words, pos)
            print(deps.print_conll())
            print()
        
