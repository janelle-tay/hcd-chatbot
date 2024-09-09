from flask import Flask, request, jsonify, render_template, send_from_directory, session

import chatbot
from chatbot import *

app = Flask(__name__, static_folder="dist")
app.secret_key = os.getenv("FLASK_SECRET_KEY")
rpa = chatbot.instantiate_llm_model()  # Initialize with the default client


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_public_files(path):
    # Check if the file exists in the dist directory
    if path and "." in path:
        try:
            return send_from_directory(app.static_folder, path)
        except Exception:
            # Return a 404 if the file is not found
            return jsonify({"error": "Not found"}), 404

    # Otherwise, serve the Vite app
    return send_from_directory(app.static_folder, "index.html")


# Serve static assets (e.g., JS, CSS)
@app.route("/assets/<path:path>")
def serve_static(path):
    return send_from_directory("dist/assets", path)


def is_authenticated():
    return session.get("authenticated", False)


@app.route("/auth/verify", methods=["POST"])
def verify():
    if is_authenticated():
        return jsonify(ok=True)

    return jsonify(ok=False), 401


@app.route("/auth/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    correct_username = os.getenv("ADMIN_USERNAME")
    correct_password = os.getenv("ADMIN_PASSWORD")
    if username == correct_username and password == correct_password:
        session["authenticated"] = True
        return jsonify(ok=True)
    else:
        return jsonify(ok=False, message="Incorrect username or password"), 401


@app.route("/select_client", methods=["POST"])
def select_client():
    global rpa
    client = request.form.get("client")
    rpa = chatbot.instantiate_llm_model(client)
    return jsonify({"message": f"Client selected: {client}"}), 200


@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.form.get("user_input")
    rpa.query(user_input)  # Get response from chatbot

    # Check the last message's type and access content accordingly
    last_message = rpa.conversation_manager.conversations.messages[-1]

    if isinstance(last_message, GeminiChatMessage):
        bot_response = last_message.parts  # Access 'parts' for Gemini
    else:
        bot_response = last_message.content  # Access 'content' for OpenAI

    return jsonify({"response": bot_response}), 200


@app.route("/save_chat", methods=["POST"])
def save_chat():
    filename = request.form.get("filename")

    try:
        # Save the chat history to the Downloads folder
        rpa.save_chat_history(filename)
        return (
            jsonify(
                {
                    "status": "success",
                    "message": f"Chat history saved successfully as {filename} in Downloads folder",
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route("/reset_chat", methods=["POST"])
def reset_chat():
    try:
        rpa.conversation_manager.reset_conversation()  # Reset the conversation history
        return jsonify({"message": "Chat history has been reset."}), 200
    except AttributeError:
        return jsonify({"message": "Failed to reset chat history."}), 500


@app.route("/update_prompt", methods=["POST"])
def update_prompt():
    new_prompt = request.form.get(
        "prompt", ""
    ).strip()  # Get the prompt from form and remove any extra whitespace

    if not new_prompt:  # If the prompt is empty or just whitespace
        # Optionally: Set a default prompt or keep it empty
        new_prompt = (
            "Default system prompt"  # Replace with an appropriate default if desired
        )

    try:
        # Update the system prompt for the current RolePlayAgent instance
        rpa.system_prompt = new_prompt
        rpa.conversation_manager.add_system_message(new_prompt)
        return (
            jsonify({"status": "success", "message": "Prompt updated successfully."}),
            200,
        )
    except Exception as e:
        return (
            jsonify(
                {"status": "error", "message": f"Failed to update prompt: {str(e)}"}
            ),
            500,
        )


if __name__ == "__main__":
    app.run(debug=True)
