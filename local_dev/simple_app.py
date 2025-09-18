import os
import logging
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format=\'%(asctime)s - %(levelname)s - %(message)s\')

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize OpenAI client
client = openai.OpenAI()

# Load knowledge base
with open("/home/ubuntu/knowledge_base.md", "r", encoding="utf-8") as f:
    knowledge_base = f.read()

# The chat history will be a list of tuples (user_message, ai_message)
chat_history = []

# --- Helper Functions ---

def log_interaction(user_message, ai_message):
    """Log the interaction with basic reasoning."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Basic reasoning analysis
    reasoning = ""
    if \'?\' in ai_message:
        reasoning = "Asked a goal-oriented follow-up question to guide the user."
    elif any(phrase in ai_message.lower() for phrase in [\'i suggest\', \'your next step\', \'you should\', \'consider\']):
        reasoning = "Provided actionable coaching advice."
    elif any(phrase in ai_message.lower() for phrase in [\'great\', \'excellent\', \'well done\', \'keep going\']):
        reasoning = "Offered motivational encouragement."
    else:
        reasoning = "Answered a business-related question with informative content."
    
    log_entry = f"[{timestamp}] User: {user_message}\\nAnna: {ai_message}\\nReasoning: {reasoning}\\n{\'=\'*50}\\n"
    
    # Write to log file
    with open("/home/ubuntu/anna_coach/interaction_log.txt", "a", encoding="utf-8") as f:
        f.write(log_entry)
    
    # Also log to console
    logging.info(f"User: {user_message}")
    logging.info(f"Anna: {ai_message}")
    logging.info(f"Reasoning: {reasoning}")

def generate_response(user_message, chat_history):
    """Generate a response using OpenAI with knowledge base context."""
    
    # Format chat history
    history_text = ""
    for human_msg, ai_msg in chat_history[-3:]:  # Keep last 3 exchanges for context
        history_text += f"User: {human_msg}\\nAnna: {ai_msg}\\n\\n"
    
    # Create the prompt
    system_prompt = f"""You are Anna, an AI entrepreneurship coach. Your goal is to support first-time entrepreneurs by answering business-related questions, giving motivational nudges, and helping them take actionable steps forward.

PERSONALITY & APPROACH:
- Be helpful, empathetic, and goal-oriented
- Always try to guide the user towards actionable steps
- Ask goal-oriented follow-up questions when appropriate
- When asking a follow-up question, briefly explain why you are asking it (e.g., "I\'m asking this because...")
- Keep responses concise but encouraging
- End your response with either a question or a suggestion for an actionable step

KNOWLEDGE BASE (Use this information to answer questions):
{knowledge_base}

Please respond as Anna, the AI entrepreneurship coach. If the user\'s question relates to topics in the knowledge base, use that information. If not, provide helpful general entrepreneurship advice and guide them toward actionable next steps."""

    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    # Add conversation history
    for human_msg, ai_msg in chat_history[-3:]:
        messages.append({"role": "user", "content": human_msg})
        messages.append({"role": "assistant", "content": ai_msg})
    
    # Add current message
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="gemini-2.5-flash", # Changed model to a supported one
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Error generating response: {e}")
        return "I apologize, but I encountered an error while processing your request. Could you please rephrase or try again? In the meantime, I suggest taking a moment to clarify what specific aspect of entrepreneurship you\'d like to explore."

# --- API Endpoints ---

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    global chat_history
    data = request.get_json()
    user_message = data.get("message")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Generate response
    ai_message = generate_response(user_message, chat_history)

    # Update chat history
    chat_history.append((user_message, ai_message))

    # Log interaction with reasoning
    log_interaction(user_message, ai_message)

    return jsonify({"response": ai_message})

@app.route("/reset", methods=["POST"])
def reset_chat():
    """Reset the chat history."""
    global chat_history
    chat_history = []
    logging.info("Chat history reset")
    return jsonify({"message": "Chat history reset successfully"})

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "message": "Anna AI Coach is running"})

if __name__ == "__main__":
    app.run(host=\'0.0.0.0\', port=5001, debug=False)


