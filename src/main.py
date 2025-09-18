"""
src/main.py

Rewritten from the original file. Key improvements:
- Fixes knowledge base path (reads knowledge_base.md from repo root)
- Loads environment variables via python-dotenv 
- Safer OpenAI client setup (reads OPENAI_API_KEY from env)
- Configurable model/temperature via env vars
- Better error handling and logging
"""

import os
import logging
import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai
from dotenv import load_dotenv

# Load environment variables from .env if available
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format=r'%(asctime)s - %(levelname)s - %(message)s'
)

# Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# OpenAI setup
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logging.warning("OPENAI_API_KEY is not set. OpenAI requests will fail until you set this environment variable.")
else:
    # set openai.api_key for compatibility with different openai client setups
    openai.api_key = OPENAI_API_KEY

# Create OpenAI client 
try:
    client = openai.OpenAI()
except Exception as e:
    # Fallback: some environments use `openai` module directly with functions
    logging.warning(f"Could not instantiate openai.OpenAI() client: {e}. Continuing with module-level usage.")
    client = openai  # still attempt to call openai.ChatCompletion or similar if needed

# Repo-root-aware paths
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
KNOWLEDGE_BASE_PATH = os.path.join(REPO_ROOT, "knowledge_base.md")
INTERACTION_LOG_PATH = os.path.join(REPO_ROOT, "interaction_log.txt")

# Load knowledge base (gracefully handle missing file)
try:
    with open(KNOWLEDGE_BASE_PATH, "r", encoding="utf-8") as f:
        knowledge_base = f.read()
    logging.info(f"Loaded knowledge base from {KNOWLEDGE_BASE_PATH}")
except FileNotFoundError:
    knowledge_base = ""
    logging.warning(f"knowledge_base.md not found at {KNOWLEDGE_BASE_PATH}. Continuing with empty knowledge base.")

# Simple in-memory chat history (list of tuples). For production, use per-session storage or DB.
chat_history = []

# Configuration via environment variables
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.4"))
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
CHAT_HISTORY_KEEP = int(os.getenv("CHAT_HISTORY_KEEP", "100"))  # how many exchanges to keep globally

# --- Helper functions ---

def _safe_write_log(path: str, content: str):
    """Ensure path exists and append content."""
    try:
        # parent dir should exist (repo root). Open in append mode.
        with open(path, "a", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        logging.error(f"Failed to write interaction log to {path}: {e}")

def log_interaction(user_message: str, ai_message: str):
    """Log the interaction with simple reasoning metadata."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Basic reasoning classification
    reasoning = ""
    if '?' in ai_message and not ai_message.strip().endswith("?"):
        # if the assistant asked a follow-up question (heuristic)
        reasoning = "Asked a goal-oriented follow-up question to guide the user."
    elif any(phrase in ai_message.lower() for phrase in ['i suggest', 'your next step', 'you should', 'consider']):
        reasoning = "Provided actionable coaching advice."
    elif any(phrase in ai_message.lower() for phrase in ['great', 'excellent', 'well done', 'keep going']):
        reasoning = "Offered motivational encouragement."
    else:
        reasoning = "Answered a business-related question with informative content."

    log_entry = (
        f"[{timestamp}] User: {user_message}\n"
        f"Anna: {ai_message}\n"
        f"Reasoning: {reasoning}\n"
        + ("=" * 50) + "\n"
    )

    _safe_write_log(INTERACTION_LOG_PATH, log_entry)

    logging.info(f"User: {user_message}")
    logging.info(f"Anna: {ai_message}")
    logging.info(f"Reasoning: {reasoning}")

def _build_system_prompt():
    """Return the system prompt that instructs the assistant persona and includes the knowledge base."""
    system_prompt = f"""You are Anna, an AI entrepreneurship coach. Your goal is to support first-time entrepreneurs by answering business-related questions, giving motivational nudges, and helping them take actionable steps forward.

PERSONALITY & APPROACH:
- Be helpful, empathetic, and goal-oriented
- Always try to guide the user towards actionable steps
- Ask goal-oriented follow-up questions when appropriate
- When asking a follow-up question, briefly explain why you are asking it (e.g., "I'm asking this because...")
- Keep responses concise but encouraging
- End your response with either a question or a suggestion for an actionable step

KNOWLEDGE BASE (Use this information to answer questions):
{knowledge_base}

Please respond as Anna, the AI entrepreneurship coach. If the user's question relates to topics in the knowledge base, use that information. If not, provide helpful general entrepreneurship advice and guide them toward actionable next steps."""
    return system_prompt

def generate_response(user_message: str, history: list):
    """
    Generate a response using the OpenAI client.
    Keeps the last 3 exchanges in the prompt for context (configurable).
    Returns the assistant's text reply (string).
    """
    # Keep global chat_history bounded
    if len(chat_history) > CHAT_HISTORY_KEEP:
        # drop oldest entries
        del chat_history[0 : (len(chat_history) - CHAT_HISTORY_KEEP)]

    # Build messages list for chat API
    messages = []
    messages.append({"role": "system", "content": _build_system_prompt()})

    # include last N exchanges from provided history (we use last 3 exchanges)
    for human_msg, ai_msg in history[-3:]:
        messages.append({"role": "user", "content": human_msg})
        messages.append({"role": "assistant", "content": ai_msg})

    # current user message
    messages.append({"role": "user", "content": user_message})

    # Call the OpenAI chat completions endpoint in a guarded way
    try:
        # Preferred: using client.chat.completions.create (newer OpenAI client style)
        if hasattr(client, "chat") and hasattr(client.chat, "completions"):
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                temperature=OPENAI_TEMPERATURE,
                max_tokens=OPENAI_MAX_TOKENS
            )
            # typical shape: response.choices[0].message.content
            try:
                return response.choices[0].message.content
            except Exception:
                # fallback to other possible shapes (string content)
                return getattr(response.choices[0], "text", str(response))
        else:
            # Fallback if client is the openai module (older API)
            if hasattr(openai, "ChatCompletion"):
                legacy_resp = openai.ChatCompletion.create(
                    model=OPENAI_MODEL,
                    messages=messages,
                    temperature=OPENAI_TEMPERATURE,
                    max_tokens=OPENAI_MAX_TOKENS
                )
                return legacy_resp.choices[0].message.get("content") or legacy_resp.choices[0].text
            else:
                raise RuntimeError("OpenAI client does not expose a chat completion interface in this environment.")
    except Exception as e:
        logging.error(f"Error generating response from OpenAI: {e}", exc_info=True)
        # Helpful fallback message that still guides the user
        return (
            "I apologize — I couldn't generate a response right now. "
            "Could you please rephrase or ask a smaller, more specific question? "
            "If you'd like, try asking about one step of your idea validation process."
        )

# --- API endpoints ---

@app.route("/")
def index():
    """Render the main UI (templates/index.html)."""
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    """Accepts JSON: { "message": "<user message>" } and returns { "response": "<assistant reply>" }"""
    global chat_history
    data = request.get_json(silent=True) or {}
    user_message = data.get("message") if isinstance(data, dict) else None

    if not user_message or not isinstance(user_message, str) or not user_message.strip():
        return jsonify({"error": "No message provided"}), 400

    user_message = user_message.strip()

    # Generate AI response
    ai_message = generate_response(user_message, chat_history)

    # Update history
    chat_history.append((user_message, ai_message))

    # Log interaction (writes to repo-root/interaction_log.txt)
    try:
        log_interaction(user_message, ai_message)
    except Exception as e:
        logging.error(f"Failed to log interaction: {e}")

    return jsonify({"response": ai_message})

@app.route("/reset", methods=["POST"])
def reset_chat():
    """Reset the in-memory chat history (for the prototype)."""
    global chat_history
    chat_history = []
    logging.info("Chat history has been reset.")
    return jsonify({"message": "Chat history reset successfully"})

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "message": "Anna AI Coach is running"})

# Run the app
if __name__ == "__main__":
    # port can come from environment (useful for deployments)
    port = int(os.getenv("PORT", "5000"))
    # Do not enable debug=True in production
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
