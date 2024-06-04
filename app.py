import ollama
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import webbrowser
import threading

app = Flask(__name__)
CORS(app)

history = []

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/ollama', methods=['POST'])
def ollama_predict():
    input_data = request.get_json()

    history.append({'role': 'user', 'content': input_data['message']})

    response = ollama.chat(model='llama3', messages=history)
    print(response['message']['content'])

    history.append({'role': 'assistant', 'content': response['message']['content']})
    return jsonify(response)

def open_browser():
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    threading.Timer(1.5, open_browser).start()
    app.run()
