import ollama
from flask import Flask, render_template
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import webbrowser
import threading

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

history = []

@app.route('/')
def home():
    return render_template('home.html')

@socketio.on('user_message')
def handle_user_message(data):
    input_message = data['message']
    history.append({'role': 'user', 'content': input_message})

    def stream_response():
        stream = ollama.chat(model='llama3', messages=history, stream=True)
        for chunk in stream:
            response_chunk = chunk['message']['content']
            emit('bot_message', {'message': response_chunk})

        emit('bot_message', {'message': '<END><END><END>'})
    
    stream_response()

def open_browser():
    webbrowser.open('http://127.0.0.1:4000')

if __name__ == '__main__':
    threading.Timer(1.5, open_browser).start()
    socketio.run(app, host="0.0.0.0", port=4000, debug=True)
