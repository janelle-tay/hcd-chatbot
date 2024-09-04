from flask import Flask, request, jsonify, render_template
import chatbot
from chatbot import *

app = Flask(__name__)
rpa = chatbot.instantiate_llm_model()  # Initialize with the default client

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/select_client', methods=['POST'])
def select_client():
    global rpa
    client = request.form.get('client')
    rpa = chatbot.instantiate_llm_model(client)
    return jsonify({"message": f"Client selected: {client}"}), 200

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form.get('user_input')
    rpa.query(user_input)  # Get response from chatbot

    # Check the last message's type and access content accordingly
    last_message = rpa.conversation_manager.conversations.messages[-1]

    if isinstance(last_message, GeminiChatMessage):
        bot_response = last_message.parts  # Access 'parts' for Gemini
    else:
        bot_response = last_message.content  # Access 'content' for OpenAI

    return jsonify({"response": bot_response}), 200

@app.route('/save_chat', methods=['POST'])
def save_chat():
    filename = request.form.get('filename')
    
    try:
        # Save the chat history to the Downloads folder
        rpa.save_chat_history(filename)
        return jsonify({"status": "success", "message": f"Conversation saved successfully as {filename} in Downloads folder"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/reset_chat', methods=['POST'])
def reset_chat():
    try:
        rpa.conversation_manager.reset_conversation() # Reset the conversation history
        return jsonify({"message": "Chat history has been reset."}), 200
    except AttributeError:
        return jsonify({"message": "Failed to reset chat history."}), 500

if __name__ == '__main__':
    app.run(debug=True)
