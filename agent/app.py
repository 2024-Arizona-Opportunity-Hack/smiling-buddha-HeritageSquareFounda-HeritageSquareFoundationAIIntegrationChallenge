from flask import Flask, request, jsonify
import json
import asyncio
from Igraph import ask_chat  # Assuming you have a similar OpenAI module in Python

app = Flask(__name__)



app = Flask(__name__, static_folder='build', static_url_path='')


@app.route('/')
def home():
    return make_response(open('build/index.html').read())

# Flask route for handling requests
@app.route('/api', methods=['POST'])
async def chat_handler():
    try:
        if not request.data:
            return jsonify({"error": "No request body"}), 400

        body = request.get_json()
        message = body.get('message')
        chat_history = body.get('chatHistory')

        if not message or not chat_history:
            return jsonify({"error": "Missing required fields"}), 400

        response = await ask_chat({'message': message, 'chatHistory': chat_history})

        return jsonify({"output" : response.get("output")})

    except Exception as err:
        print(f"Error: {err}")
        return jsonify({"error": "An error occurred"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)



    


# async def read_stream(reader, response_stream: ResponseStream):
#     try:
#         while True:
#             chunk = await reader.read()
#             if chunk is None:
#                 # End of stream
#                 response_stream.end()
#                 break
            
#             value = chunk.get("response", {}).get("delta", "")
#             print(value)
#             response_stream.write(value)
#     except Exception as error:
#         print(f'Stream reading error: {error}')

