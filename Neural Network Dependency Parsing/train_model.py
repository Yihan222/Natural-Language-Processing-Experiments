
from extract_training_data import FeatureExtractor
import sys
import numpy as np
import tensorflow as tf
# to resolve some conflicts of using keras directly
from keras import Sequential
from keras.layers import Flatten, Embedding, Dense

def build_model(word_types, pos_types, outputs, input_l=6, embedding_dim=32):
    # TODO: Write this function for part 3
    model = Sequential()
    #model.add(...)
    # 1. Embedding layer: input_dimension is possible words: word_types
    #                     output_dimension is 32
    #                     input_length = 6
    model.add(Embedding(word_types, embedding_dim, input_length=input_l))
    # 2. Flatten layer
    model.add(Flatten())
    # 3. Dense layer: units = 100,
    #                 relu activation
    model.add(Dense(100, activation='relu'))
    # 4. Dense layer : units = 10,
    #                  relu activation
    model.add(Dense(10, activation='relu'))
    # 5. Output layer
    model.add(Dense(outputs, activation='softmax'))
    model.compile(tf.keras.optimizers.Adam(learning_rate=0.01), loss="categorical_crossentropy")
    return model


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
    print("Compiling model.")
    model = build_model(len(extractor.word_vocab), len(extractor.pos_vocab), len(extractor.output_labels))
    inputs = np.load(sys.argv[1])
    outputs = np.load(sys.argv[2])
    print("Done loading data.")
   
    # Now train the model
    model.fit(inputs, outputs, epochs=5, batch_size=100)
    
    model.save(sys.argv[3])
