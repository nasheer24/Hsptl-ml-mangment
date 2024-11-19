
#dense chatbot

import nltk
from nltk.stem import WordNetLemmatizer
import json
import pickle
import numpy as np
from tensorflow.keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.optimizers import SGD
import random
import matplotlib.pyplot as plt
nltk.download('punkt')

words = []
classes = []
documents = []
ignore_words = ['?', '!']
data_file = open('first_aid.json').read()
intents = json.loads(data_file)

lemmatizer = WordNetLemmatizer()

for intent in intents['intents']:
    for pattern in intent['patterns']:
        w = nltk.word_tokenize(pattern)
        words.extend(w)
        documents.append((w, intent['tag']))
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_words]
words = sorted(list(set(words)))
classes = sorted(list(set(classes)))

pickle.dump(words, open('words1.pkl', 'wb'))
pickle.dump(classes, open('classes1.pkl', 'wb'))

training = []
output_empty = [0] * len(classes)

for doc in documents:
    bag = []
    pattern_words = doc[0]
    pattern_words = [lemmatizer.lemmatize(word.lower()) for word in pattern_words]
    for w in words:
        bag.append(1) if w in pattern_words else bag.append(0)

    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1

    training.append([np.array(bag), np.array(output_row)])

train_x = [item[0] for item in training]
train_y = [item[1] for item in training]

train_x = np.array(train_x)
train_y = np.array(train_y)

model = Sequential()
model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(train_y[0]), activation='softmax'))

sgd = SGD(learning_rate=0.01, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

hist = model.fit(train_x, train_y, epochs=200, batch_size=5, verbose=1)
final_training_accuracy = hist.history['accuracy'][-1]
print(f'Final Training Accuracy: {final_training_accuracy * 100:.2f}%')
plt.plot(hist.history['accuracy'])
plt.title('Model Accuracy using Dense neural network')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.show()

model.save('chatbot_model1.h5', hist)
print("Model created")  
