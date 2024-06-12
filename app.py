import ollama
from flask import Flask, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import webbrowser
import threading
import os
import random

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

history = []
chats_dir = "./static/chat_history"

is_new_chat = True
curr_chat_name = "New"
sep_token = "<cQQZNJHzaLMfdSb9J9YZ>"
user_text_delim_token = "<vXoVfjWCkL3ZADvInB7I>"

@app.route('/')
def home():
    global history
    history = []
    return render_template('home.html')

@socketio.on('get_chat_names')
def get_chat_names():
    names = os.listdir(chats_dir)
    names = [name.replace('.json', '').replace('_', ' ').replace(".txt", "").title() for name in names]
    emit('chat_names', {'message': "|".join(names)})

@socketio.on('get_chat')
def get_chat(data):
    global is_new_chat

    is_new_chat = False
    chat_name = data['chatName']
    chat_file = os.path.join(chats_dir, chat_name.replace(" ","_") + '.txt')

    with open(chat_file, 'r') as f:
        global history

        file_content = f.read()
        messages = file_content.split(sep_token)
        messages = [message.split(user_text_delim_token) for message in messages]

        if len(messages[-1]) == 1:
            messages = messages[:-1]

        history = [{'role': message[0].replace("\n", ""), 'content': message[1]} for message in messages]
        print(len(history))
        
        for message in history:
            emit('chat_message', {'role': message['role'], 'content': message['content']})

@socketio.on('new_chat')
def new_chat():
    global is_new_chat
    is_new_chat = True

@socketio.on('clear_chat')
def clear_chat():
    global history
    history = []
    emit('chat_cleared')    
    
@socketio.on('user_message')
def handle_user_message(data):
    input_message = data['message']
    history.append({'role': 'user', 'content': input_message})

    def stream_response():
        stream = ollama.chat(model='llama3', messages=history, stream=True)
        res = ''
        for chunk in stream:
            response_chunk = chunk['message']['content']
            emit('assistant_message', {'message': response_chunk})
            res += response_chunk

        emit('assistant_message', {'message': '<END><END><END>'})
        history.append({'role': 'assistant', 'content': res})

        # global is_new_chat
        # global curr_chat_name

        # if is_new_chat:
        #     curr_chat_name = str(random.randint(0, 1000))
        #     is_new_chat = False

        # chat_file = os.path.join(chats_dir, curr_chat_name + '.txt')
        
        # if not os.path.exists(chat_file):
        #     with open(chat_file, 'w') as f:
        #         f.write('')

        # with open(chat_file, 'a') as f:
        #     f.write(f"user{user_text_delim_token}{input_message}\n{sep_token}\n")
        #     f.write(f"assistant{user_text_delim_token}{res}\n{sep_token}\n")

        # all_text = ''
        # for message in history:
        #     all_text += f"{message['content']}\n"

        # heading_generator_prompt = all_text + "\n============\nabove is a prompt. Write a small 3 word description of the prompt. Dont say anything else"

        # response = ollama.generate(model='llama3', prompt=heading_generator_prompt)
        # heading = response['response'].replace(" ", "_").replace('"', "").replace("'", "")

        # new_chat_file = os.path.join(chats_dir, heading + '.txt')
        # if os.path.exists(new_chat_file):
        #     new_chat_file = os.path.join(chats_dir, heading + str(random.randint(0, 1000)) + '.txt')

        # os.rename(chat_file, new_chat_file)

    stream_response()

def open_browser():
    webbrowser.open('http://127.0.0.1:4000')

if __name__ == '__main__':
    threading.Timer(1.5, open_browser).start()
    socketio.run(app, host="0.0.0.0", port=4000, debug=True)
