import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np
from keras.models import load_model
import json
import random
import tkinter as tk
from tkinter import Text, Scrollbar, Entry, Button
import speech_recognition as sr
from tkinter import messagebox

model = load_model('chatbot_model1.h5')
intents = json.loads(open('first_aid.json').read())
words = pickle.load(open('words1.pkl','rb'))
classes = pickle.load(open('classes1.pkl','rb'))

recognizer = sr.Recognizer()

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bow(sentence, words, show_details=True):
    sentence_words = clean_up_sentence(sentence)
    bag = [0]*len(words)
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s:
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % w)
    return np.array(bag)

def predict_class(sentence, model):
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

def getResponse(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if(i['tag']== tag):
            result = random.choice(i['responses'])
            break
    return result

def extract_link(response):
    # Extract link from HTML response
    start_index = response.find('href="') + 6
    end_index = response.find('">', start_index)
    link = response[start_index:end_index]
    return link



def chatbot_response(msg):
    ints = predict_class(msg, model)
    res = getResponse(ints, intents)

    # Check if the response contains a link
    if '<a' in res and 'href="' in res:
        link = extract_link(res)
        ChatLog.config(state=tk.NORMAL)
        ChatLog.insert(tk.END, f"Bot: {res.replace(link, 'click here')}\n\n")
        ChatLog.tag_add("clickable", "1.0", "end")
        ChatLog.tag_config("clickable", foreground="blue", underline=True)
        ChatLog.tag_bind("clickable", "<Button-1>", lambda event, link=link: open_link(link))
    else:
        ChatLog.config(state=tk.NORMAL)
        ChatLog.insert(tk.END, f"Bot: {res}\n\n")

    ChatLog.config(state=tk.DISABLED)
    ChatLog.yview(tk.END)

def open_link(link):
    import webbrowser
    webbrowser.open(link)




def send():
    msg = EntryBox.get("1.0",'end-1c').strip()
    EntryBox.delete("0.0", tk.END)

    if msg != '':
        ChatLog.config(state=tk.NORMAL)
        ChatLog.insert(tk.END, "You: " + msg + '\n\n')
        ChatLog.config(foreground="#442265", font=("Verdana", 12 ))

        chatbot_response(msg)

        ChatLog.config(state=tk.DISABLED)
        ChatLog.yview(tk.END)

def send_voice_input():
    with sr.Microphone() as source:
        print("Say something:")
        audio = recognizer.listen(source)

    try:
        voice_input = recognizer.recognize_google(audio)
        print("Voice Input:", voice_input)
        ChatLog.config(state=tk.NORMAL)
        ChatLog.insert(tk.END, "You: " + voice_input + '\n\n')
        ChatLog.config(foreground="#442265", font=("Verdana", 12))

        chatbot_response(voice_input)

        ChatLog.config(state=tk.DISABLED)
        ChatLog.yview(tk.END)
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print(f"Error with the speech recognition service: {e}")


# Create GUI window
base = tk.Tk()
base.title("KITSChatbot")
base.geometry("400x500")
base.resizable(width=False, height=False)

# Create Chat window
ChatLog = Text(base, bd=0, bg="white", height="8", width="50", font="Arial",)
ChatLog.config(state=tk.DISABLED)

# Bind scrollbar to Chat window
scrollbar = Scrollbar(base, command=ChatLog.yview, cursor="heart")
ChatLog['yscrollcommand'] = scrollbar.set

# Create Button to send message
SendButton = Button(base, font=("Verdana", 12, 'bold'), text="Send", width="12", height=5,
                    bd=0, bg="#32de97", activebackground="#3c9d9b", fg='#ffffff',
                    command=send)

# Create Button to send voice input
VoiceButton = Button(base, font=("Verdana", 12, 'bold'), text="Voice", width="12", height=5,
                     bd=0, bg="#32de97", activebackground="#3c9d9b", fg='#ffffff',
                     command=send_voice_input)

# Create the box to enter message
EntryBox = Text(base, bd=0, bg="white", width="29", height="5", font="Arial")

# Place all components on the screen
scrollbar.place(x=376, y=6, height=386)
ChatLog.place(x=6, y=6, height=386, width=370)
EntryBox.place(x=6, y=401, height=90, width=265)
SendButton.place(x=265, y=401, height=45)
VoiceButton.place(x=265, y=451, height=45)

base.mainloop()