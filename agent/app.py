from flask import Flask, request, jsonify
import json
import asyncio
from Lgraph import ask_chat
from flask_cors import CORS


app = Flask(__name__, static_folder='build', static_url_path='')
CORS(app)



@app.route('/')
def home():
    return make_response(open('build/index.html').read())

# Flask route for handling requests
@app.route('/api', methods=['POST'])
async def chat_handler():
    try:
        # print(request.data)
        # print(request.get_json())


        if not request.data:
            return jsonify({"error": "No request body"}), 400

        body = request.get_json()
        message = body.get('message')
        chat_history = body.get('ChatHistory', [])

        print(message)
        print(chat_history)

        # if not message or not chat_history:
        #     return jsonify({"error": "Missing required fields"}), 400

        response = await ask_chat({'message': message, 'chatHistory': chat_history})

        return jsonify({"output" : response.get("output")})

    except Exception as err:
        print(f"Error: {err}")
        return jsonify({"error": "An error occurred"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)

