from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from openai import OpenAI
import os

app = Flask(__name__, static_folder="")  # Serve static files from root
CORS(app)

# Get API key from environment variable
API_KEY = os.environ.get("OPENAI_API_KEY")
MODEL = "openai/gpt-oss-20b:free"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY
)

@app.route("/")
def index():
    # Serve index.html from the same folder
    index_path = os.path.join(os.path.dirname(__file__), "index.html")
    return send_file(index_path)

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_message = request.json.get("message")

        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": user_message}],
            extra_body={"reasoning": {"enabled": True}}
        )

        msg = response.choices[0].message

        messages = [
            {"role": "user", "content": user_message},
            {
                "role": "assistant",
                "content": msg.content,
                "reasoning_details": getattr(msg, "reasoning_details", None)
            },
            {"role": "user", "content": "Continue your reasoning."}
        ]

        final_response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            extra_body={"reasoning": {"enabled": True}}
        )

        reply = final_response.choices[0].message.content
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})
